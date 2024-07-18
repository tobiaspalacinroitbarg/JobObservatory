import requests
from bs4 import BeautifulSoup
import pandas as pd
from threads import threads_computrabajo
from funcs import get_contrato_ct, get_jornada_ct, get_modalidad_ct, get_salario_ct, get_pais, get_provincia_ct,get_localidad_ct

def get_links(url:str, headers:dict, link_pais:str):
    """
    La función obtiene todos los links de las ofertas de empleo.
    """
    payload = ""

    lista_links:list[str] = []
    
    querystring = {}
    
    i:int = 1

    lista_links:[str] = []

    while True:
            response = requests.request("GET", url+f"&p={i}", json=payload, headers=headers, params=querystring)
            if response.status_code == 403:
                return 1004
            else:
                soup = BeautifulSoup(response.text, "lxml")
                links_raw = soup.find_all("a", {"class":"js-o-link fc_base"}, href=True)
                if links_raw:
                    lista_links.extend([link_pais+link["href"] for link in links_raw])
                    print(f"Listo los links de la página {i}")
                    i+=1
                else:
                    print(f"En la iteración {i} terminó")
                    break
    return lista_links

def get_oferta(url, headers=None):
    """
    La función toma todos los datos de una oferta dada su url y los headers.
    """
    querystring = {"responsive": "true"}

    payload = ""

    data = {}

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    if response.status_code == 403:
        return 1005
    else:
        try:
            soup = BeautifulSoup(response.text, "lxml")
            tags_raw = soup.find_all("span", {"class": "tag base mb10"})
            data["detalles_empleo"] = set([tag.text for tag in tags_raw ]) if tags_raw else None
            link_empresa = soup.find("a", {"class": "dIB fs16 js-o-link"})
            data["link_empresa"] = link_empresa.get("href") if link_empresa else None 
            desc_empresa = soup.find("p", {"show-more": True}) 
            data["descripcion_empresa"] = desc_empresa.get_text() if desc_empresa else None
            rating_empresa = soup.find("p", {"class": "fs50 fwB lh1 tc"})
            data["rating"] = rating_empresa.get_text() if rating_empresa else None
            cant_eval = soup.find("p", {"class": "fc_aux mt5 fs16"})
            data["cant_eval"] = cant_eval.get_text() if cant_eval else None
            fecha =  soup.find("p", {"class": "fc_aux fs13"})
            data ["fecha_publ"] = fecha.get_text() if fecha else None
            p_elements = soup.find_all("p", {"class": "fs18 fwB"})[:4]
            p_names = ["p_amb_trab", "p_sal_prest", "p_oport_carr", "p_direc_general"]
            if p_elements:
                for i, p_z in enumerate(p_elements):
                    data[p_names[i]] = p_z.get_text() if p_z else None
            data["link_ct"] = url
            titulo = soup.find("h1",{"class":"fwB fs24 mb5 box_detail w100_m"})
            data["titulo"] = titulo.text if titulo else None
            pal = soup.find("p",{"class":"fc_aux fs13 mbB mtB"})
            data["palabras_clave"]= pal.get_text() if pal else None
            name_jobLoc_raw = soup.find("p",{"class":"fs16"})
            name_jobLoc = name_jobLoc_raw.text if name_jobLoc_raw else None
            data["ubicacion"] = name_jobLoc.split("-")[-1].strip() if name_jobLoc else None
            data["empresa"]="-".join(name_jobLoc.split("-")[:-1]).strip() if name_jobLoc else None
            raw_descr = soup.find_all("p",{"class":"mbB"})
            data["descripcion"]= raw_descr[0].get_text() if raw_descr and raw_descr[0] else None
            raw_req = soup.find("ul",{"class":"disc mbB"})
            data["requisitos"] = raw_req.get_text() if raw_req else None
            if data["titulo"] is None or not url:
                return 2002
        except Exception as e:
            print(f"ERROR {e}")
            
    return data

def main_computrabajo():
    link_paises:dict[str] = {
    1:["Nicaragua","https://ni.computrabajo.com/"],
    2:["Panamá","https://pa.computrabajo.com/"],
    3:["Honduras","https://hn.computrabajo.com/"],
    4:["Costa Rica","https://cr.computrabajo.com/"],
    5:["Guatemala","https://gt.computrabajo.com/"],
    6:["El Salvador","https://sv.computrabajo.com/"]}
    estados_paises = {
    "Nicaragua": ["managua", "leon", "esteli", "matagalpa", "chinandega", "chontales", "granada", "nueva-segovia", "masaya", "jinotega", "rivas", "atlantico-sur", "carazo", "boaco", "extranjero", "rio-san-juan", "atlantico-norte", "madriz", "managua-en-managua", "leon-en-leon"],
    "Panamá":["panama", "panama-oeste", "colon", "chiriqui", "cocle", "veraguas", "darien", "herrera", "los-santos", "bocas-del-toro", "extranjero", "panama-en-panama", "san-miguelito", "colon-en-colon", "arraijsan", "david", "la-chorrera", "penonome", "santiago", "anton"],
    "Honduras":["cortes", "francisco-morazan", "atlantida", "comayagua", "olancho", "choluteca", "colon", "copan", "yoro", "islas-de-la-bahia", "el-paraiso", "santa-barbara", "valle", "intibuca", "extranjero", "ocotepeque", "lempira", "la-paz", "san-pedro-sula", "distrito-central"],
    "Costa Rica":["san-jose", "alajuela", "heredia", "guanacaste", "cartago", "puntarenas", "limon", "san-jose-en-san-jose", "alajuela-en-alajuela", "heredia-en-heredia", "escazu", "curridabat", "montes-de-oca", "santa-ana", "belen", "liberia", "cartago-en-cartago", "goicoechea", "puntarenas-en-puntarenas", "desamparados"],
    "Guatemala":["guatemala", "escuintla", "quetzaltenango", "sacatepequez", "huehuetenango","peten", "zacapa", "alta-verapaz", "chimaltenango", "chiquimula","izabal", "suchitepequez", "san-marcos", "retalhuleu", "santa-rosa","jutiapa", "quiche", "el-progreso", "solola", "jalapa"],
    "El Salvador":["san-salvador", "la-libertad", "san-miguel", "santa-ana", "chalatenango","la-paz", "sonsonate", "cabañas", "usulutan", "la-union", "cuscatlan","ahuachapan", "san-vicente", "morazan"]
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
    } 
    
    lista_links_final = []

    for id_pais in link_paises.keys():

        pais:str = link_paises[id_pais][0]

        link_pais:str = link_paises[id_pais][1]

        for l in estados_paises[pais]:

            print(f"Comienza el scraping de {l.lower()}, {pais}.")
            
            lista_links = get_links(f"{link_pais}/empleos-en-{l}?", link_pais=link_pais, headers=headers)

            if isinstance(lista_links, int):
                return lista_links
            else:
                for link in lista_links:
                    lista_links_final.append(link)
    lista_links_final_2 = [elemento for elemento in lista_links_final if isinstance(elemento, dict)]
    data_list = []
    for link in lista_links_final_2:
        data = get_oferta(data, headers=headers)
        data_list.append(data)
    df = pd.DataFrame(data_list)
    df = df.drop_duplicates(subset="link_ct")
    df["detalles_empleo"] = df["detalles_empleo"].apply(list)
    df["tipo_contrato"] = df["detalles_empleo"].apply(lambda x: get_contrato_ct(x))
    df["jornada"] = df["detalles_empleo"].apply(lambda x: get_jornada_ct(x))
    df["salario"] = df["detalles_empleo"].apply(lambda x: get_salario_ct(x))
    df["modalidad"] = df["detalles_empleo"].apply(lambda x: get_modalidad_ct(x))
    df["pais"] = df["link_ct"].apply(lambda x: get_pais(x))
    df["localidad"] = df["ubicacion"].astype(str).apply(lambda x: get_localidad_ct(x))
    df["provincia"] = df["ubicacion"].astype(str).apply(lambda x: get_provincia_ct(x))

    df["p_amb_trab"] = df["p_amb_trab"].str.replace(',', '.').astype(float).fillna(0)
    df["p_sal_prest"] = df["p_sal_prest"].str.replace(',', '.').astype(float).fillna(0)
    df["p_oport_carr"] = df["p_oport_carr"].str.replace(',', '.').astype(float).fillna(0)
    df["p_direc_general"] = df["p_direc_general"].str.replace(',', '.').astype(float).fillna(0)
    df["rating"] = df["rating"].str.replace(',', '.').astype(float).fillna(0)
    df['cant_eval'] = df['cant_eval'].str.extract('(\d+)').fillna(0).astype(int)
    df.drop(axis="columns", columns=["ubicacion","detalles_empleo"], inplace=True)
    return df



   