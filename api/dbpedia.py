from functools import wraps
import SPARQLWrapper

ENDPOINT = 'http://dbpedia.org/sparql'
dbpedia_sparql = SPARQLWrapper.SPARQLWrapper(ENDPOINT)
theatres_city='dbc:Theatres_in_'
pr_country='dbc:Former_theatres_in_'

def prefix_uri(func):
    @wraps(func)
    def prefix(*args, **kwargs):
        if args[0].startswith('http://dbpedia.org/resource/'):
            modified_uri = (args[0].replace('http://dbpedia.org/resource/', 'dbr:')
                            .replace('(', '\(')
                            .replace(')', '\)'))

            new_args = (modified_uri,) + args[1:]
            return func(*new_args, **kwargs)
        return lambda x: None
    return prefix


def search_theatres(name, theatre, lang='ru'):
    city=name.replace(' ', '_')
    countries = find_country(city, lang)
    n_country = ''
    for country in countries:
      co = country['countryLabel']['value']
      n_country = co.replace(' ', '_')
    former = pr_country + n_country
    theatres = theatre+city

    query = '''select distinct ?theatre ?tLabel ?thumbnail (SAMPLE(?site) AS ?site) where 
    {?theatre dct:subject %s.
    ?theatre rdfs:label ?tLabel.
    OPTIONAL {?theatre dbo:thumbnail ?thumbnail.}
    OPTIONAL {?theatre dbo:wikiPageExternalLink ?site.}
    FILTER (lang(?tLabel)="en").
    ''' % (theatres)

    if former:
        query += '\nFILTER NOT EXISTS {?theatre dct:subject %s}.' % (former)

    query += '} ORDER BY ?tLabel '

    dbpedia_sparql.setQuery(query)

    dbpedia_sparql.setReturnFormat(SPARQLWrapper.JSON)
    return dbpedia_sparql.query().convert()['results']['bindings']


def find_country(city, lang='ru'):

    query = '''SELECT ?countryLabel 
    WHERE {?city rdfs:label "%s"@%s.
    ?city rdf:type dbo:Place; dbo:country ?country.
    ?country rdfs:label ?countryLabel.
    FILTER(langMatches(lang(?countryLabel),"en"))
    } 
    ''' % (city, lang)
    dbpedia_sparql.setQuery(query)

    dbpedia_sparql.setReturnFormat(SPARQLWrapper.JSON)
    return dbpedia_sparql.query().convert()['results']['bindings']


@prefix_uri
def get_bio(uri):
    query = '''SELECT ?abstract ?tLabel ?comment ?geo ?thumbnail (MIN((?site)) as ?site) ?wp WHERE {
        %s dbo:abstract ?abstract.
        %s rdfs:label ?tLabel.
        OPTIONAL {%s rdfs:comment ?comment}
        OPTIONAL {%s geo:geometry ?geo}
        OPTIONAL {%s dbo:thumbnail ?thumbnail}
        OPTIONAL {%s dbo:wikiPageExternalLink ?site.}
        OPTIONAL {%s foaf:isPrimaryTopicOf ?wp.}
        FILTER(lang(?abstract) = 'en')
        FILTER(lang(?tLabel) = 'en')
        FILTER(lang(?comment) = 'en')
        } 
    '''% (uri, uri, uri, uri, uri, uri, uri)

    dbpedia_sparql.setQuery(query)

    dbpedia_sparql.setReturnFormat(SPARQLWrapper.JSON)
    data = dbpedia_sparql.query().convert()['results']['bindings']
    return data[0] if len(data) > 0 else {}


def get_label(uri):
    query = '''
        SELECT * WHERE {
        %s rdfs:label ?tLabel.
        FILTER(lang(?tLabel) = 'en')}
    '''% (uri)
    dbpedia_sparql.setQuery(query)
    dbpedia_sparql.setReturnFormat(SPARQLWrapper.JSON)
    return dbpedia_sparql.query().convert()['results']['bindings']

@prefix_uri
def get_peoples(uri):
    results = []
    label = get_label(uri)
    for i in label:
        name_theatre = i['tLabel']['value']
    word_in_name_th = name_theatre.replace('.', '').replace(',', '').replace('(', '').replace(')', '').split(" ")
    for word in list(word_in_name_th):
        if len(word)<3:
            word_in_name_th.remove(word)

    for word in word_in_name_th:
        query ='''
        SELECT DISTINCT 
        ?person 
        (SAMPLE(?name) as ?name) 
        (SAMPLE(?date) as ?date)  
        ?thumbnail 
        WHERE {
        ?person rdf:type dbo:Person.
        ?person foaf:surname ?surname.
        ?person foaf:name ?name.
        ?surname bif:contains '%s'.
        ?person dbo:birthDate ?date.
        OPTIONAL { ?person dbo:thumbnail ?thumbnail }
        FILTER(lang(?surname) = 'en') 
        FILTER(lang(?name) = 'en') 
        FILTER NOT EXISTS {dbr:%s rdf:type dbo:Place}
        }
        ''' % (word, word)

        dbpedia_sparql.setQuery(query)
        dbpedia_sparql.setReturnFormat(SPARQLWrapper.JSON)
        results += dbpedia_sparql.query().convert()['results']['bindings']
    return results if len(results) > 0 else None

