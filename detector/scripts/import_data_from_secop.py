import os
import re
import unidecode
import requests
import unidecode
from datetime import date
import sys
from .utils.dict_ciudades import *
# from ..detector

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "../detector.settings")


def replaceIgnoreCase(real_text, old_text, new_text):
    redata = re.compile(re.escape(old_text), re.IGNORECASE)
    return redata.sub(new_text, real_text)


def get_entidad(entidad, departamento, municipio):
    partes = [unidecode.unidecode(x.strip()) for x in entidad.split("-")]
    posibles = []
    # print partes
    for parte in partes:
        parte = unidecode.unidecode(parte)
        part = replaceIgnoreCase(parte, departamento, "")
        part = replaceIgnoreCase(part, municipio, "")
        if part not in "":
            posibles.append(parte.encode("utf8"))

    if len(posibles) == 0:
        return municipio.encode("utf8")
    elif len(posibles) == 1:
        return unicode(posibles[0]).encode("utf8")
    else:
        return " - ".join(posibles).encode("utf8")


today = date.today()
contador = 0


def item2db(item, categoria, subcategoria):
    try:
        titulo = unicode(item.getElementsByTagName("title")[0].childNodes[0].data)
        titulo = "Proceso " + titulo[11:]
        descripcion = item.getElementsByTagName("description")[0].childNodes[0].data

        link = item.getElementsByTagName("link")[0].childNodes[0].data

        author = item.getElementsByTagName("author")[0].childNodes[0].data
        author = author.replace(" ", "")

        departamento = item.getElementsByTagName("category")[0].childNodes[0].data
        departamento = unidecode.unidecode(departamento)

        pos_end_entidad = item.getElementsByTagName("description")[0].childNodes[0].data.index("</strong>")
        entidad = descripcion[8:pos_end_entidad]

        municipio = get_municipio(entidad)
        if type(municipio) is not str:
            return
        entidad = get_entidad(entidad, departamento, municipio)

        pos_end_entidad += 9
        post_start_precio_estimado = descripcion.index("<strong>", pos_end_entidad) + 8 + 17

        precio_estimado = descripcion[post_start_precio_estimado:-9]
        precio_estimado = int(precio_estimado.replace(",", ""))

        titulo = unidecode.unidecode(titulo)

        municipio = unidecode.unidecode(municipio)

        descripcion = unidecode.unidecode(descripcion)

        BR = descripcion.index("<br/>") + 5
        descripcion_filtrado = descripcion[BR:]
        descripcion_filtrado = descripcion_filtrado[:descripcion_filtrado.index("<br />")]
        descripcion_filtrado = descripcion_filtrado.replace(")", " ")
        descripcion_filtrado = descripcion_filtrado.replace("(", " ")

        elementos_sql = (
        titulo, descripcion, link, author, departamento, municipio, entidad, precio_estimado, today, categoria,
        subcategoria, descripcion_filtrado)

        global contador
        contador = contador + 1
    except sqlite3.IntegrityError:
        pass
    except Exception as ex:
        tipo = str(type(ex).__name__)
        descripcion = str(ex.args)
        data = link
        sql = "INSERT INTO errores(tipo, descripcion,info) values(?,?,?)"
        c.execute(sql, (tipo, descripcion, data))
        print
        tipo + ":> " + descripcion


def makepeticion(elemento):
    try:
        R = requests.get(elemento["url"], verify=False)
        XML = parseString(R.content).documentElement

        for item in XML.getElementsByTagName("item"):
            item2db(item, elemento["cat"], elemento["subcat"])

    except requests.exceptions.RequestException as e:
        print
        e
        print
        "Error con la conexion a internet"
        sys.exit(1)

if __name__== "__main__":
    for rss in RSS:
        makepeticion(rss)
    print(contador+" licitaciones nuevas agregadas")