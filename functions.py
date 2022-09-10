from bs4 import BeautifulSoup


def ss_to_hhmmss(segundos):
    horas = int(segundos / 60 / 60)
    segundos -= horas*60*60
    minutos = int(segundos/60)
    segundos -= minutos*60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

def status(sell_condition):                          
        split_text = sell_condition.text.split(' ')
        for num in range(0,len(split_text)):
            if ('Nuevo' in split_text[num]): 
               str='Nuevo'
               return str                              
            if ('Usado' in split_text[num] and len(split_text)==1):
               str='Usado' 
               return str                                
            if ('Usado' in split_text[num] and len(split_text)>1):
               str='Usado'
               return str

def qty(sell_condition):
        split_text = sell_condition.text.split(' ')
        for num in range(0,len(split_text)):
            if ('Nuevo' in split_text[num]): 
               for num in range(0,len(split_text)):
                    if ('vendidos' in split_text[num]):
                        return int(split_text[num - 1])                                                 
            
            if ('Usado' in split_text[num]):
                for num in range(0,len(split_text)):
                    if ('vendidos' in split_text[num]):
                        return int(split_text[num - 1])


def return_ubication(text,var):
    soup = BeautifulSoup(text,'html.parser')
    text_soup = soup.prettify()
    split_text = text_soup.split(',')
    
    for num in range(0,len(split_text)):
        if var == 'provincia':
             return split_text[len(split_text)-1].strip()
        if var == 'localidad':
             return split_text[len(split_text)-2].strip()