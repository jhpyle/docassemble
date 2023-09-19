import re
import subprocess

__all__ = ['language_list', 'lang_name', 'get_fonts']


def language_list():
    return [('ab', 'Abkhazian'), ('aa', 'Afar'), ('af', 'Afrikaans'), ('ak', 'Akan'), ('sq', 'Albanian'), ('am', 'Amharic'), ('ar', 'Arabic'), ('an', 'Aragonese'), ('hy', 'Armenian'), ('as', 'Assamese'), ('av', 'Avaric'), ('ae', 'Avestan'), ('ay', 'Aymara'), ('az', 'Azerbaijani'), ('bm', 'Bambara'), ('ba', 'Bashkir'), ('eu', 'Basque'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('bh', 'Bihari languages'), ('bi', 'Bislama'), ('bs', 'Bosnian'), ('br', 'Breton'), ('bg', 'Bulgarian'), ('my', 'Burmese'), ('ca', 'Catalan'), ('ch', 'Chamorro'), ('ce', 'Chechen'), ('zh', 'Chinese'), ('cu', 'Church Slavic'), ('cv', 'Chuvash'), ('kw', 'Cornish'), ('co', 'Corsican'), ('cr', 'Cree'), ('hr', 'Croatian'), ('cs', 'Czech'), ('da', 'Danish'), ('dv', 'Dhivehi'), ('nl', 'Dutch'), ('dz', 'Dzongkha'), ('en', 'English'), ('eo', 'Esperanto'), ('et', 'Estonian'), ('ee', 'Ewe'), ('fo', 'Faroese'), ('fj', 'Fijian'), ('fi', 'Finnish'), ('fr', 'French'), ('ff', 'Fulah'), ('gl', 'Galician'), ('lg', 'Ganda'), ('ka', 'Georgian'), ('de', 'German'), ('gn', 'Guarani'), ('gu', 'Gujarati'), ('ht', 'Haitian'), ('ha', 'Hausa'), ('he', 'Hebrew'), ('hz', 'Herero'), ('hi', 'Hindi'), ('ho', 'Hiri Motu'), ('hu', 'Hungarian'), ('is', 'Icelandic'), ('io', 'Ido'), ('ig', 'Igbo'), ('id', 'Indonesian'), ('ia', 'Interlingua (International Auxiliary Language Association)'), ('ie', 'Interlingue'), ('iu', 'Inuktitut'), ('ik', 'Inupiaq'), ('ga', 'Irish'), ('it', 'Italian'), ('ja', 'Japanese'), ('jv', 'Javanese'), ('kl', 'Kalaallisut'), ('kn', 'Kannada'), ('kr', 'Kanuri'), ('ks', 'Kashmiri'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('ki', 'Kikuyu'), ('rw', 'Kinyarwanda'), ('ky', 'Kirghiz'), ('kv', 'Komi'), ('kg', 'Kongo'), ('ko', 'Korean'), ('kj', 'Kuanyama'), ('ku', 'Kurdish'), ('lo', 'Lao'), ('la', 'Latin'), ('lv', 'Latvian'), ('li', 'Limburgan'), ('ln', 'Lingala'), ('lt', 'Lithuanian'), ('lu', 'Luba-Katanga'), ('lb', 'Luxembourgish'), ('mk', 'Macedonian'), ('mg', 'Malagasy'), ('ms', 'Malay (macrolanguage)'), ('ml', 'Malayalam'), ('mt', 'Maltese'), ('gv', 'Manx'), ('mi', 'Maori'), ('mr', 'Marathi'), ('mh', 'Marshallese'), ('el', 'Modern Greek (1453-)'), ('mn', 'Mongolian'), ('na', 'Nauru'), ('nv', 'Navajo'), ('ng', 'Ndonga'), ('ne', 'Nepali (macrolanguage)'), ('nd', 'North Ndebele'), ('se', 'Northern Sami'), ('no', 'Norwegian'), ('nb', 'Norwegian Bokmål'), ('nn', 'Norwegian Nynorsk'), ('ny', 'Nyanja'), ('oc', 'Occitan (post 1500)'), ('oj', 'Ojibwa'), ('or', 'Oriya (macrolanguage)'), ('om', 'Oromo'), ('os', 'Ossetian'), ('pi', 'Pali'), ('pa', 'Panjabi'), ('fa', 'Persian'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('ps', 'Pushto'), ('qu', 'Quechua'), ('ro', 'Romanian'), ('rm', 'Romansh'), ('rn', 'Rundi'), ('ru', 'Russian'), ('sm', 'Samoan'), ('sg', 'Sango'), ('sa', 'Sanskrit'), ('sc', 'Sardinian'), ('gd', 'Scottish Gaelic'), ('sr', 'Serbian'), ('sh', 'Serbo-Croatian'), ('sn', 'Shona'), ('ii', 'Sichuan Yi'), ('sd', 'Sindhi'), ('si', 'Sinhala'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('so', 'Somali'), ('nr', 'South Ndebele'), ('st', 'Southern Sotho'), ('es', 'Spanish'), ('su', 'Sundanese'), ('sw', 'Swahili (macrolanguage)'), ('ss', 'Swati'), ('sv', 'Swedish'), ('tl', 'Tagalog'), ('ty', 'Tahitian'), ('tg', 'Tajik'), ('ta', 'Tamil'), ('tt', 'Tatar'), ('te', 'Telugu'), ('th', 'Thai'), ('bo', 'Tibetan'), ('ti', 'Tigrinya'), ('to', 'Tonga (Tonga Islands)'), ('ts', 'Tsonga'), ('tn', 'Tswana'), ('tr', 'Turkish'), ('tk', 'Turkmen'), ('tw', 'Twi'), ('ug', 'Uighur'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('uz', 'Uzbek'), ('ve', 'Venda'), ('vi', 'Vietnamese'), ('vo', 'Volapük'), ('wa', 'Walloon'), ('cy', 'Welsh'), ('fy', 'Western Frisian'), ('wo', 'Wolof'), ('xh', 'Xhosa'), ('yi', 'Yiddish'), ('yo', 'Yoruba'), ('za', 'Zhuang'), ('zu', 'Zulu')]


def lang_name(language):
    for item in language_list():
        if language == item[0]:
            return item[1]
    return language


def get_fonts(language):
    arguments = ['fc-list', ':lang=' + language, 'family', 'file']
    try:
        completed_process = subprocess.run(arguments, timeout=600, check=False, capture_output=True)
        result = completed_process.returncode
        if result != 0:
            error_message = completed_process.stderr.decode()
    except subprocess.TimeoutExpired:
        result = 1
        error_message = "call to fc-list timed out"
    if result == 0:
        return sorted([x.split(': ') for x in re.sub(',', ', ', completed_process.stdout.decode()).split("\n") if x != ''], key=lambda y: y[1])
    return [error_message]
