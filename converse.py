import re
import int_to_roman as ir
def converse(inp):
    '''
        The idea is to provide a simple chatbot for the
        roman - integral converter. Basic idea is strip
        all vowels from text, homogenise the case
        followed by a simple string comparison to formulate
        an appropriate response
    '''
    try:
        inp = int(inp)
        return ir.intToRoman(inp)
    except:
        pass

    try:
        helper_var =[re.sub('[aeiou]+','','translate'),
                     re.sub('[aeiou]+','',inp).lower(),
                     int(re.search('(?<![\d.])[0-9]+(?![\d.])',inp).group(0))]
        # I'm not quite sure I understand this regex myself
        # but the idea is to match digits which are neither directly
        # followed nor directly preceded by a '.'
        # ie, match a integer input but not a float
        #[0-9]+ matches one or more digits
        # and the lookahead disallows a digit, following a dot 
        #print helper_var
    except:
            #print 'Oops, I did\'nt catch your number!'
            return None
    
    if helper_var[0] in helper_var[1]:
        try:
            return ir.intToRoman(helper_var[2])
        except:
            print 'Oops! I didn\'t recognize it! Please, try again'
    return None
    
print 'Hi, I\'m a very simple bot. I convert arabic numerals to Roman numerals.'
print 'Pleased to meet you :)'
print

while(True):
    inp = raw_input('Please enter a number to convert to Roman Representation :')
    ans = converse(inp)
    if ans is None:
        print 'Oops! I didn\'t recognize it! Please, try again'
    else:
        print 'The Roman representation of your number is',ans
