
proxy_use = True
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
}

path_to_chromedriver = '/root/telegram_bot/chromedriver'

site_url = 'https://sedeclave.dgt.gob.es/WEB_NCIT_CONSULTA/solicitarCita.faces'
api_key = ''
gkey = '6LeK_-kZAAAAAEqP9TZnX-js2ldWjNxNnvReXsOY'

data_base = 'database.db'

telegram_token = ''

proxy_file = '/root/telegram_bot/Webshare 100 proxies.txt'
admin_id = 000 # write your telegram id

chat_list = [] # list of telegram ids


office_city = '#publicacionesForm\:oficina > optgroup:nth-child(4) > option:nth-child(2)'
proc = '#publicacionesForm\:tipoTramite > option:nth-child(4)'
country_list = ['#publicacionesForm\:pais > option:nth-child(4)', '#publicacionesForm\:pais > option:nth-child(4)', '#publicacionesForm\:pais > option:nth-child(8)']

submit_button = '#publicacionesForm\:j_id70 > input'

