'''
//      #####   json_validator.py   #####
//
// Python utility Script to validate JSON RTD String
// For Historical data, use DebugView.
//
// Performace penalty for Plugin to validate every permutation is unnecessary,
// as a well written CLIENT=APP already performs checks on RTD. 
//
///////////////////////////////////////////////////////////////////////
// Author: NSM51
// https://github.com/ideepcoder/Rtd_Ws_AB_plugin/
// https://forum.amibroker.com/u/nsm51/summary
// 
// Any use of this source code must include the above notice, 
// in the user documentation and internal comments to the code.
'''


import json

## Insert RTD json string in '' quotes to validate
js = '[{"n":"SYM3","d":20250127,"t":230908,"o":189.45,"h":196.32,"l":181.89,"c":194.59,"v":1212,"bp":186.71,"as":10},\
       {"n":"SYM2","d":20250127,"t":230908,"o":189.45,"h":196.32,"l":181.89,"c":194.59,"v":1212,"ap":186.71,"bs":10}]'

###############
# Fields used by RTD json

Field_str           = [ 'n' ]
Field_num_reqd      = [ 'o', 'h', 'l', 'c' ]
Field_num_optional  = [ 'v', 'oi', 'x1', 'x2', 's', 'pc', 'bs', 'bp', 'as', 'ap', 'do', 'dh', 'dl' ]


def check_str_reqd( f, r ):
    if f in r:
        if not isinstance( r[f], str ):
            print( f"{f} not str in \n{r}" ); return False
    else:
        print( f"{f} not found in \n{r}" ); return False

    return True


def check_num_reqd( f, r ):
    if f in r:
        if not isinstance( r[f], (int, float) ):
            print( f"{f} not NUM in \n{r}" ); return False
    else:
        print( f"{f} not found in \n{r}" ); return False

    return True


def check_num_opt( f, r ):
    if f in r:
        if not isinstance( r[f], (int, float) ):
            print( f"{f} not NUM in \n{r}" ); return False

    return True


'''
Function to validate type of mandatory & optional fields
'''
def json_rtd_validate( js:str ):
    
    if js.startswith('[{"n"'): print(f"\nString MATCH = ok")
    else: print(f"\nString MATCH failed"); return
    
    try:
        jo = json.loads( js )
        print( f"Json parsing = ok" )
    except Exception as e:
        print( e ); return
    

    if isinstance( jo, list):
        print("Outer Array = ok\n")
    else:
        print( f"Not Array of Quotes"); return


    i = 0;
    for r in jo:

        if not isinstance( r, dict ): print(f"record should be dict"); return

        ## test mandatory 'n' and type
        if not check_str_reqd( 'n', r ): return

        ## OHLC, test mandatory and type
        for ro in Field_num_reqd:
            if not check_num_reqd( ro, r ): return

        ## Optionals, test type
        for ro in Field_num_optional:
            if not check_num_opt( ro, r ): return

        ## Date
        if 'd' in r:
            if type( r['d'] ) is not int:
                print( f"d not int \n{r}" ); return

            if 't' in r:
                if type( r['t'] ) is not int :
                    print( f"t not int \n{r}" ); return
            else:
                print( f"t is required with d in \n{r}"); return

        elif 'u' in r:
            if type( r['u'] ) is not int :
                print( f"u not int \n{r}" ); return

        elif 'g' in r:
            if type( r['g'] ) is not int :
                print( f"g not int \n{r}" ); return

        else: print( f"d/u/g not found in \n{r}" ); return
        
        print( f"record {i} = ok" ); i += 1 

    return 1


#### main()
if __name__ == '__main__':
    
    if json_rtd_validate( js ):
        print( f"\nFinal validation = OK\n")
    else:
        print( f"\nFinal validation = FAILED\n" )

    #print( js )        ## print original string

