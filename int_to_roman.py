numberMap = {
    1000:'M',
    900:'CM',
    500:'D',
    400:'CD',
    100:'C',
    90:'XC',
    50:'L',
    40:'XL',
    10:'X',
    9:'IX',
    5:'V',
    4:'IV',
    1:'I'
    }

def floorKey(d,k):
    '''
    returns the largest key less than or equal to
    the given key in the provided dictionary
    Utility fucntion for intToRoman(n)
    '''
    if d.has_key(k):
        return k
    else:
        try:
            return max(key for key in d if key < k)
        except:
            return None
    
def intToRoman(n):
    '''
    Converts an arabic number to a Roman numeral
    Given a number, checks if the number is already present in a number mapping
    if true, return that number
    if false add the largest key smaller than the given number to the roman
    repr of preceding number
    '''
    is_present = floorKey(numberMap,n)
    #print "number",n
    if (n == is_present):
        return numberMap[is_present]
    return numberMap[is_present]+ intToRoman(n-is_present)

if __name__=="__main__":
    while(True):
        inp = raw_input('Please enter a number to convert to Roman Representation :')
        try:
            inp = int(inp)
            print 'The Roman representation of this number is :',str(intToRoman(inp))
        except:
            print 'Sorry, I only understand arabic numerals!'
