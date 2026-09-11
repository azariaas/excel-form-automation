"""Preenchimento e envio de um formulário web via Selenium."""

from __future__ import annotations

import logging
import time

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    MoveTargetOutOfBoundsException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from automation.config import TargetConfig

logger = logging.getLogger(__name__)

PAGE_LOAD_WAIT_SECONDS = 15
POST_SUBMIT_WAIT_SECONDS = 3
SUBMIT_CONFIRMATION_WAIT_SECONDS = 10

# Trechos comuns em URLs/elementos de páginas de sucesso após envio de formulário.
SUCCESS_URL_HINTS = ("sucesso", "success", "obrigado", "thank")
SUCCESS_SELECTORS = (
    "[class*='success']",
    "[id*='success']",
    "[class*='sucesso']",
    "[id*='sucesso']",
)


def start_driver(headless: bool = False) -> webdriver.Chrome:
    """Inicializa o navegador Chrome controlado pelo Selenium."""
    options = Options()
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless=new")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


class FormSubmissionError(Exception):
    """Erro ao preencher ou enviar o formulário."""


def _neutralize_blocking_element(driver: webdriver.Chrome, element) -> bool:
    """Se algo estiver sobreposto ao botão (banner fixo, chat, etc.), desativa o clique nele.

    Retorna True se encontrou e neutralizou algo, False se não havia nada bloqueando
    (ou se o próprio "bloqueio" era o botão ou um filho dele).
    """
    try:
        blocked_html = driver.execute_script(
            "const el = arguments[0];"
            "const r = el.getBoundingClientRect();"
            "const x = r.x + r.width / 2;"
            "const y = r.y + r.height / 2;"
            "const top = document.elementFromPoint(x, y);"
            "if (!top || top === el || el.contains(top)) return null;"
            "top.style.pointerEvents = 'none';"
            "return top.outerHTML.slice(0, 200);",
            element,
        )
    except WebDriverException:
        return False

    if blocked_html:
        logger.warning("Elemento sobreposto ao botão de envio foi desativado temporariamente: %s", blocked_html)
        return True
    return False


def _click_robust(driver: webdriver.Chrome, wait: WebDriverWait, element) -> None:
    """Clica no botão de envio de forma resiliente a elementos sobrepostos (fixos ou não)."""
    driver.execute_script(
        "arguments[0].scrollIntoView({behavior: 'instant', block: 'center', inline: 'center'});",
        element,
    )
    time.sleep(0.3)

    try:
        wait.until(EC.element_to_be_clickable(element))
    except TimeoutException:
        pass  # segue tentando; o próprio clique revela se algo ainda bloqueia

    try:
        element.click()
        return
    except ElementClickInterceptedException:
        logger.warning("Clique interceptado no botão de envio — verificando o que está por cima dele.")

    # Elemento fixo (banner, chat, botão "voltar ao topo") não some com scroll — desativa o clique nele.
    if _neutralize_blocking_element(driver, element):
        time.sleep(0.2)
        try:
            element.click()
            return
        except ElementClickInterceptedException:
            pass

    # ActionChains move o "mouse" fisicamente até o elemento antes de clicar.
    try:
        ActionChains(driver).move_to_element(element).pause(0.2).click(element).perform()
        return
    except (ElementClickInterceptedException, MoveTargetOutOfBoundsException):
        logger.warning("ActionChains também falhou — usando fallback via JavaScript.")

    # Último recurso: dispara o clique diretamente no DOM via JavaScript.
    driver.execute_script("arguments[0].click();", element)


def _wait_for_submission(driver: webdriver.Chrome, original_url: str) -> bool:
    """Confirma que o envio ocorreu observando mudança de URL ou indicador de sucesso na página."""
    confirm_wait = WebDriverWait(driver, SUBMIT_CONFIRMATION_WAIT_SECONDS)

    try:
        confirm_wait.until(lambda d: d.current_url != original_url)
        return True
    except TimeoutException:
        pass

    for selector in SUCCESS_SELECTORS:
        try:
            confirm_wait.until(EC.presence_of_element_located(("css selector", selector)))
            return True
        except TimeoutException:
            continue

    return False


def fill_and_submit(driver: webdriver.Chrome, target: TargetConfig, data: dict[str, str]) -> None:
    """Preenche os campos configurados para o alvo e envia o formulário."""
    wait = WebDriverWait(driver, PAGE_LOAD_WAIT_SECONDS)

    try:
        driver.get(target.url)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    except TimeoutException as exc:
        raise FormSubmissionError(f"A página não carregou a tempo: {target.url}") from exc

    for field, selector in target.field_selectors.items():
        value = data.get(field, "")
        try:
            element = driver.find_element("css selector", selector)
            element.clear()
            if value:
                element.send_keys(value)
        except NoSuchElementException as exc:
            raise FormSubmissionError(
                f"Campo '{field}' não encontrado com o seletor '{selector}'."
            ) from exc

    if target.consent_checkbox_selector:
        try:
            checkbox = driver.find_element("css selector", target.consent_checkbox_selector)
            if not checkbox.is_selected():
                checkbox.click()
        except NoSuchElementException:
            logger.warning("Checkbox de consentimento não encontrado para %s — seguindo sem marcá-lo.", target.code)

    try:
        submit_button = driver.find_element("css selector", target.submit_button_selector)
    except NoSuchElementException as exc:
        raise FormSubmissionError("Botão de envio não encontrado.") from exc

    original_url = driver.current_url
    try:
        _click_robust(driver, wait, submit_button)
    except WebDriverException as exc:
        raise FormSubmissionError(f"Não foi possível clicar no botão de envio: {exc}") from exc

    if not _wait_for_submission(driver, original_url):
        raise FormSubmissionError(
            "O clique no botão foi realizado, mas não foi possível confirmar que o formulário foi enviado."
        )

    time.sleep(POST_SUBMIT_WAIT_SECONDS)
