import asyncio
import time
import warnings
import telebot
import zipfile
import requests
import json
from telebot.async_telebot import AsyncTeleBot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from sql_scripts import *
from config import *


bot = AsyncTeleBot(telegram_token)


@bot.message_handler(commands=['start'])
async def start(message):
    try:
        user_id = message.chat.id
        try:
            await bot.send_message(user_id, "Hello, this is a notifier bot!\nPlease wait for information about new procedures, the bot is actively searching.")
        except telebot.apihelper.ApiException as e:
            print(e)
    except Exception as e:
        print("Error in /start block {}".format(e))
        await asyncio.sleep(0.1)


@bot.message_handler(commands=['launch_bot'])
async def launch_bot(message):
    try:
        user_id = message.chat.id

        if user_id == admin_id:
            try:
                if get_bot_work_status() == "True":
                    try:
                        await bot.send_message(user_id, "The bot is already up and running.\n"
                                                    "Wait for new information.\n"
                                                    "To stop the bot, use the /stop_bot command.")
                    except telebot.apihelper.ApiException as e:
                        print(e)
                else:
                    change_work_status("True")
                    try:
                        await bot.send_message(user_id, "🤖 You have launched the bot. 🤖\n"
                                                    "To stop the bot, use the /stop_bot command.")
                    except telebot.apihelper.ApiException as e:
                        print(e)
            except Exception as e:
                print("Error in /launch block #2\n{}".format(e))
                await asyncio.sleep(0.1)
        else:
            try:
                await bot.send_message(user_id, "You do not have permission to use this command.")
            except telebot.apihelper.ApiException as e:
                print(e)
    except Exception as e:
            print(e)


@bot.message_handler(commands=['stop_bot'])
async def launch_bot(message):
    try:
        user_id = message.chat.id

        if user_id == admin_id:
            try:
                if get_bot_work_status() == "False":
                    try:
                        await bot.send_message(user_id, "The bot is currently disabled.\n"
                                                    "To launch, use the /launch_bot command.")
                    except telebot.apihelper.ApiException as e:
                        print(e)
                else:
                    change_work_status("False")
                    try:
                        await bot.send_message(user_id, "🤖 You have stopped the bot. 🤖\n"
                                                    "To launch, use the /launch_bot command.")
                    except telebot.apihelper.ApiException as e:
                        print(e)
            except Exception as e:
                print("Error in /stop block #2\n{}".format(e))
                await asyncio.sleep(0.1)
        else:
            try:
                await bot.send_message(user_id, "You do not have permission to use this command.")
            except telebot.apihelper.ApiException as e:
                print(e)
    except Exception as e:
        print("Error in /stop block #1\n{}".format(e))
        await asyncio.sleep(0.1)


class Click_Obj():
    def __init__(self, wait):
        self.wait = wait

    def office(self, office_city):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, office_city))).click()

    def proc(self, proc):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, proc))).click()

    def city(self, city):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, city))).click()

    def submit(self, submit_button):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, submit_button))).click()


async def get_chromedriver(proxy_ip, proxy_port, proxy_login, proxy_pass, use_proxy=False, user_agent=None, headers=None):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (proxy_ip, proxy_port, proxy_login, proxy_pass)


    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/google-chrome'
    options.add_argument('--headless=new')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = webdriver.chrome.service.Service(path_to_chromedriver)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    if use_proxy:
        pluginfile = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
    if user_agent:
        options.add_argument('--user-agent=%s' % user_agent)
        options.add_argument('--headers=%s' % json.dumps(headers))
    browser = webdriver.Chrome(service=service, options=options)
    return browser


async def captcha_post(google_sitekey, page_url):
    url = f'http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={google_sitekey}&pageurl={page_url}'
    return requests.get(url)


async def captcha_get(id):
    url = f'http://2captcha.com/res.php?key={api_key}&action=get&id={id}'
    return requests.get(url)


async def captcha_api(google_sitekey, page_url):
    resp_post = await captcha_post(google_sitekey, page_url)
    if resp_post.text[:2] == "OK":
        await asyncio.sleep(15)
        response = await captcha_get(resp_post.text[3:])
        while True:
            if response.text != "CAPCHA_NOT_READY":
                break
            await asyncio.sleep(5)
            response = await captcha_get(resp_post.text[3:])
        captcha_key = response.text[3:]
        return captcha_key


async def call_back_detect(browser):
    js_code = """
    function findRecaptchaClients() {
      if (typeof (___grecaptcha_cfg) !== 'undefined') {
        return Object.entries(___grecaptcha_cfg.clients).map(([cid, client]) => {
          const data = { id: cid, version: cid >= 10000 ? 'V3' : 'V2' };
          const objects = Object.entries(client).filter(([_, value]) => value && typeof value === 'object');

          objects.forEach(([toplevelKey, toplevel]) => {
            const found = Object.entries(toplevel).find(([_, value]) => (
              value && typeof value === 'object' && 'sitekey' in value && 'size' in value
            ));

            if (typeof toplevel === 'object' && toplevel instanceof HTMLElement && toplevel['tagName'] === 'DIV'){
                data.pageurl = toplevel.baseURI;
            }

            if (found) {
              const [sublevelKey, sublevel] = found;

              data.sitekey = sublevel.sitekey;
              const callbackKey = data.version === 'V2' ? 'callback' : 'promise-callback';
              const callback = sublevel[callbackKey];
              if (!callback) {
                data.callback = null;
                data.function = null;
              } else {
                data.function = callback;
                const keys = [cid, toplevelKey, sublevelKey, callbackKey].map((key) => `['${key}']`).join('');
                data.callback = `___grecaptcha_cfg.clients${keys}`;
              }
            }
          });
          return data;
        });
      }
      return [];
    }

    return findRecaptchaClients();
    """

    result = browser.execute_script(js_code)
    # return result[0]['callback']
    return result


async def injection(browser, captcha_key, call_back_value):
    captcha_v2 = """
    var element = document.getElementById('publicacionesForm:responseV2');
    element.value = '{capcha_key}';
    """
    grecaptchav2_script = f"{call_back_value}('{captcha_key}')"
    browser.execute_script(captcha_v2.format(capcha_key=captcha_key))
    time.sleep(3)
    browser.execute_script(grecaptchav2_script)


async def error_check(browser, office, pais):
    wait = WebDriverWait(browser, 30)

    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#cabecera')))
    time.sleep(3)

    try:
        error = soup.find('div', class_='buscadorInterno').find('li', class_='msgError').get_text().strip()
        if error:
            # print("Офіс: {}\nКраїна: {}\nАктивних процедур не знайдено.".format(office, pais))
            return error
    except:
        try:
            header = soup.find('div', class_='central')
            if header:
                browser.save_screenshot("screenshot.png")
                # print("АКТИВНУ ПРОЦЕДУРУ ЗНАЙДЕНО!\nОфіс: {}\nКраїна: {}".format(office, pais))
                return ''
        except:
            return 'error'


async def telegram_bot(error_text, office, pais):
    if len(error_text) > 0:
        pass
        # for chat_id in chat_list:
        #     await bot.send_message(chat_id, "Офіс: {}\nКраїна: {}\nТекст на сторінці:\n{}".format(office, pais, error_text))
    else:
        for chat_id in chat_list:
            try:
                await bot.send_message(chat_id, "✅ ЗНАЙДЕНО АКТИВНУ ПРОЦЕДУРУ ✅\nОфіс: {}\nКраїна: {}".format(office, pais))
                with open(f'{photo_name}', 'rb') as photo:
                    response = requests.post(
                        f'https://api.telegram.org/bot{telegram_token}/sendPhoto',
                        files={'photo': photo},
                        data={'chat_id': chat_id}
                    )
            except telebot.apihelper.ApiException as e:
                print(e)
                await asyncio.sleep(0.1)


async def captcha_post_google(google_sitekey, page_url, data_s, proxy):
    url = f'http://2captcha.com/in.php?key={api_key}&method=userrecaptcha&googlekey={google_sitekey}&pageurl={page_url}&data-s={data_s}&proxy={proxy}&proxytype={"HTTP"}'
    return requests.get(url)


async def captcha_api_google(google_sitekey, page_url, data_s, proxy):
    resp_post = await captcha_post_google(google_sitekey, page_url, data_s, proxy)
    if resp_post.text[:2] == "OK":
        time.sleep(15)
        response = await captcha_get(resp_post.text[3:])
        while True:
            if response.text != "CAPCHA_NOT_READY":
                break
            time.sleep(5)
            response = await captcha_get(resp_post.text[3:])
        captcha_key = response.text[3:]
        return captcha_key


async def injection_google(browser, captcha_key):
    element = browser.find_element(By.ID, "g-recaptcha-response")
    browser.execute_script("arguments[0].removeAttribute('style');", element)
    browser.execute_script(f"arguments[0].value = '{captcha_key}';", element)
    await asyncio.sleep(1)
    browser.execute_script("document.getElementById('captcha-form').submit();")


async def pass_bot_checking(browser, proxy_ip, proxy_port, proxy_login, proxy_password):
    wait = WebDriverWait(browser, 10)

    proxy = "{}:{}@{}:{}".format(proxy_login, proxy_password, proxy_ip, proxy_port)
    await asyncio.sleep(1)
    browser.get("https://www.google.com/")
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body')))
    site_info = await call_back_detect(browser)
    call_back, pg_url, site_key = site_info[0]['callback'], site_info[0]['pageurl'], site_info[0]['sitekey']
    element = browser.find_element(By.ID, "recaptcha")
    data_s_value = element.get_attribute("data-s")

    captcha_key = await captcha_api_google(site_key, pg_url, data_s_value, proxy)
    await injection_google(browser, captcha_key)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#L2AGLb > div'))).click()


async def parsing_selenium(browser, country):
    wait = WebDriverWait(browser, 30)
    click = Click_Obj(wait)
    click.office(office_city)
    click.proc(proc)
    click.city(country)

    await asyncio.sleep(0.2)
    pais = browser.find_element(By.CSS_SELECTOR, country).text
    office = browser.find_element(By.CSS_SELECTOR, office_city).text

    await asyncio.sleep(0.2)
    captcha_key = await captcha_api(gkey, site_url)

    await asyncio.sleep(0.2)
    call_back_value = await call_back_detect(browser)
    call_back_value = call_back_value[0]['callback']

    await asyncio.sleep(0.2)
    await injection(browser, captcha_key, call_back_value)

    await asyncio.sleep(0.2)
    click.submit(submit_button)

    await asyncio.sleep(0.2)
    error_text = await error_check(browser, office, pais)

    await asyncio.sleep(0.2)
    await telegram_bot(error_text, office, pais)


async def get_data_from_website():
    await asyncio.sleep(0.2)

    if get_bot_work_status() == "True":

        with open(proxy_file, 'r') as file:
            x = file.read()

        await asyncio.sleep(0.1)

        proxy_lst = x.split('\n')
        proxy_lst = [i for i in proxy_lst if len(i) > 0]

        await asyncio.sleep(0.1)

        count = 0
        while count != len(proxy_lst):
            proxy_ip, proxy_port, proxy_login, proxy_password = proxy_lst[count].split(':')
            await asyncio.sleep(0.1)
            browser = await get_chromedriver(proxy_ip, proxy_port, proxy_login, proxy_password, use_proxy=proxy_use, user_agent=user_agent, headers=headers)
            await asyncio.sleep(0.1)


            wait = WebDriverWait(browser, 10)

            if get_bot_work_status() == "True":
                try:
                    await pass_bot_checking(browser, proxy_ip, proxy_port, proxy_login, proxy_password)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    print(e)
                await asyncio.sleep(2)
                try:
                    browser.get("https://sede.dgt.gob.es/es/otros-tramites/cita-previa-jefaturas/index.shtml#")
                    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#aceptarcookie > a'))).click()
                except Exception as e:
                    print(e)
                try:
                    browser.get(site_url)
                    await asyncio.sleep(2)
                    for country in country_list:
                        await asyncio.sleep(0.1)
                        try:
                            await parsing_selenium(browser, country)
                        except Exception as e:
                            print(e)
                    browser.quit()
                except Exception as e:
                    print(e)
                    browser.quit()
                count += 1
            else:
                browser.quit()
                break


async def main_processes():
    try:
        while True:
            await get_data_from_website()
            await asyncio.sleep(1)
    except Exception as error:
        print(error)


async def main():
    bot_task = asyncio.create_task(bot.polling(non_stop=True, request_timeout=120))
    data_mining_task = asyncio.create_task(main_processes())

    await asyncio.gather(bot_task, data_mining_task)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
