'''
//      #####   vendor_class.py   #####
//
// Client-app Class wrapper for Broker/Vendor library for WsRtd AmiBroker Data Plugin
//
// Python Program that can be used to wrap a Broker/Vendor Library.
// Key highlights is it has a dataframe to Build Bars for base time interval.
// Data transmission works with snapshotting model
//
// This program is a template for PRODUCTION USE.
//
///////////////////////////////////////////////////////////////////////
// Author: NSM51
// https://github.com/ideepcoder/Rtd_Ws_AB_plugin/
// https://forum.amibroker.com/u/nsm51/summary
//
// Users and possessors of this source code are hereby granted a nonexclusive, 
// royalty-free copyright license to use this code in individual and commercial software.
//
// AUTHOR ( NSM51 ) MAKES NO REPRESENTATION ABOUT THE SUITABILITY OF THIS SOURCE CODE FOR ANY PURPOSE. 
// IT IS PROVIDED "AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND. 
// AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOURCE CODE, 
// INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. 
// IN NO EVENT SHALL AUTHOR BE LIABLE FOR ANY SPECIAL, INDIRECT, INCIDENTAL, OR 
// CONSEQUENTIAL DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, 
// WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, 
// ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOURCE CODE.
// 
// Any use of this source code must include the above notice, 
// in the user documentation and internal comments to the code.
'''


import time
import datetime
import pandas as pd

from Real_Vendor_Class import DataSocket    ## Your actual Vendor Class
## OR
import DataSocket


## Global variables
cdt             = 0         ## current datetime.datetime.now() object
V_DS_ctr        = 0         ## Vendor connection error counter
secTick         = 1         ## one minute bars, +ve int for minute. (1,5,15 AB supported) Later, 0=1 sec


## Global objects
vendor_ws_1     = 0         ## our class data socket instance
printDFlist     = []        ## Storage List to print symbols. Debugging.


############  Functions   ############

def GetAuthToken():
    '''use vendor code to generate API Key or Authentication Token'''

    return ""


## remember to keep updating cdt
def rcdt()->datetime.datetime:
    '''Returns as well as Updates global current-datetime variable cdt.'''

    global cdt; cdt = datetime.datetime.now();  return cdt
rcdt()


def Scdt(i=0):
    '''DT as string'''
    global cdt
    return cdt.strftime('%H:%M') if i else cdt.strftime('%H:%M:%S')


## Make Todays DateTime from TIME arguments
def makeTime( H:int=0, M:int=0, S:int=0 )->datetime.datetime:
    cdt = datetime.datetime.now()

    if isinstance( H, str) and M==0 and S==0:
        sTime = H.split(sep=':')
        H=int( sTime[0] ); M=int( sTime[1]); S=int( sTime[2] )
    return datetime.datetime( cdt.year,cdt.month,cdt.day,H,M,S )



def barSec(t:datetime.datetime): return t.hour*10000 + t.minute*100 + t.second         # second ticks

def barmin(t:datetime.datetime): return t.hour*10000 + t.minute//secTick*100*secTick    # create candle time in min

candle = barmin if secTick else barSec      ## point to candle func, for base time interval



def Rename_Symbol( s ):
    '''This is where you can perform symbol renaming'''

    return ""


class VendorDataSocket():

    def __init__(self, symbols:list, reconnect=True, rtd_type="RtdTick"):
        
        super().__init__()

        ## Some common parameters used by Vendor
        self.access_token   = GetAuthToken()
        self.reconnect      = reconnect
        self.symbols        = list( filter(None, symbols))   ## List of subscribed symbols
        self.data_type      = rtd_type

        ## Pointer for Vendor Class
        self.vendor         = None

        ## Some debugging functions to expose
        self.printMsgsF     = False
        self.debugSym       = 0
        

        ## WsRtd  DF
        ##pv=prev bar vol, wl=snapshot price, wv=snapshot vol, s=Total_daily_vol, symbol=feed_sym_name,n=sym_renamed_if_reqd
                
        self.goodtick       = int( makeTime( 9,15,0 ).timestamp())       ## timestamp filter, say skip pre-open market
        self.clsNm          = 'RTD:'
        self.dfcols         = ['symbol', 'n', 'd', 't', 'o', 'h', 'l', 'c', 'v', 'oi', 'pv', 'wl', 'wv', 's','pc','bs','bp','as','ap','do','dh','dl','ch','cp']
        self.outcols        = [          'n', 'd', 't', 'o', 'h', 'l', 'c', 'v', 'oi',                   's','pc','bs','bp','as','ap','do','dh','dl','ch','cp']
        self.ed             = {'d':int(cdt.strftime('%Y%m%d'))}         # rest init to 0

        ## init code for DataFrame
        self.df             = pd.DataFrame( columns=self.dfcols)
        self.df             = self.df.astype({'symbol':str, 'n':str, 'd':int, 't':int, 'o':float, 'h':float, 'l':float, 'c':float, 'v':int,
                                'oi':int, 'pv':int, 'wl':float, 'wv':int, 's':int, 'pc':float, 'bs':int,'bp':float,'as':int,'ap':float,
                                'do':float, 'dh':float, 'dl':float, 'ch':float,'cp':float })
        
        self.df.set_index('symbol', inplace=True )


    def on_error(self, message):
        global V_DS_ctr
        V_DS_ctr += 1
        s = f"{self.clsNm} error: {Scdt()} {message}"
        print( s )
        if V_DS_ctr > 10: print("code to take action as error counter hit")


    def on_disconnect(self, msg):
        try:
            rcdt()
            if msg['code']==200:    print(f"{self.clsNm} close: {Scdt()} {msg['message']}")
        except: print(f"{self.clsNm} close:  {Scdt()} {msg}")
        
        '''cleanup and post disconnect here'''


    def on_connect(self):
        self.subscribe_symbol( self.symbols)
        self.vendor.run_thread()                ## vendor defined function to keep it running


    def connect(self):

        ## Assign CallBack functions here for Vendor Library and start. Just a sample with expected callbacks

        self.vendor  = Real_Vendor_Class.DataSocket(
            token    = self.access_token,            
            reconnect       = self.reconnect,
            on_connect      = self.on_connect,
            on_disconnect   = self.on_disconnect,
            on_error        = self.on_error,
            on_data         = self.on_data,
            retry_connect   = 10
        )
        self.vendor.connect()           ## this is where you start you vendor's thread/class


    def addSym(self, s):
        if s not in self.symbols:   self.symbols.append( s )          ##List not really used, just keeps List of symbols and init variable
                            
        if s not in self.df.index:
            self.df.loc[s]              = 0
            self.df.at[s, 'n']          = Rename_Symbol( s )
            self.df.loc[s, self.ed.keys()] = self.ed.values()        ## easy way to assign dict


    def subscribe_symbol(self, sym:list):
        '''takes LIST of symbols to Subscribe'''
        sym = list( filter( None, sym))         # remove '' in list
        if sym == []:   return

        for s in sym: self.addSym(s)
            
        self.symbols.sort()
        self.df.sort_index( inplace=True )
        self.vendor.subscribe( symbols=sym ) #, channel=15
        print(f"{self.clsNm} subs: { ', '.join(sym) }")


    def unsubscribe_symbol(self, sym:list[str] ):
        '''takes LIST of symbols to Unsubscribe'''
        sym = list( filter( None, sym))                               # remove '' in list
        if sym == []:   return

        self.vendor.unsubscribe( symbols=sym )                        # vendor class to unsubscribe
        time.sleep(0.5)                                               # wait for round trip
        ## unsub first, then cleanup
        for s in sym:
            if s in self.symbols:
                self.symbols.remove( s )
            if s in self.df.index:
                self.df.drop(s, inplace=True)
        
        self.symbols.sort()
        self.df.sort_index( inplace=True )
        print(f"{self.clsNm} unsub: { ', '.join(sym) }")
        
    
    def disconnect(self):
        try:
            if self.vendor:  self.vendor.close_connection()
        except Exception as e:
            print(f'{self.clsNm} disconnect(): {repr(e)}')


    def on_data(self, msg):
        '''most important function that processes messages from vendor'''
        try:
            #t1 = time.perf_counter()
            if "data" in msg:
                if msg["data"] in ('stock', 'index'):             ## Example: IF message type is stock or index
                    
                    s=msg['symbol']; sf=0; tf='exch_time'         ## tf for Index/non-index symbols
                    
                    ## testing, output msg to stdio
                    if self.printMsgsF or self.debugSym==s: print( msg )
                    
                    #Filter some pre=open ticks, for example
                    if self.goodtick > msg[tf]: return

                    if msg["data"]=='stock':
                        pvol=self.df.at[s, 'pv'];   tvol=msg['total_volume']
                        if not (pvol+self.df.at[s, 'v']) < tvol: return     ## update flag=0, writeDF skips it. RETURN as NO Vol+
                        else:   sf=1; tf='last_trade_time'

                    p = msg['last_trade_price']                            # result=df.loc[s]## extract row, but loses index:not reqd                     
                    t = candle( datetime.datetime.fromtimestamp( msg[tf])) # last time, create bar time (barSec()/barMin())


                    ## Now, we Build bars of base time interval

                    if t == self.df.at[s, 't']:
                        if p > self.df.at[s, 'h']: self.df.at[s, 'h'] = p
                        if p < self.df.at[s, 'l']: self.df.at[s, 'l'] = p
                        if sf:  self.df.at[s, 'v']= tvol - pvol
                    else:
                        self.df.at[s, 'o']= self.df.at[s, 'h']= self.df.at[s, 'l']= p    ##OHL=p
                        if sf:
                            self.df.at[s, 'v']  = msg['last_traded_qty']
                            self.df.at[s, 'pv'] = tvol - msg['last_traded_qty']

                    self.df.at[s, 'c']  = p
                    self.df.at[s, 't']  = t
                    self.df.at[s, 'pc'] = msg["prev_day_close"]
                    self.df.at[s, 'do'] = msg["open_price"]                                             ## For RT Window
                    self.df.at[s, 'dh'] = msg["high_price"]; self.df.at[s, 'dl'] = msg["low_price"]     ## Day Open, Day High, Day Low 
                    self.df.at[s, 'ch'] = msg["ch"];         self.df.at[s, 'cp'] = msg["chp"]           ## perc_change and change
                    
                    ## Make bars for indices or tradable instruments
                    if sf:
                        self.df.at[s, 's']  = tvol
                        self.df.at[s, 'bs'] = msg['bid_size']; self.df.at[s,'bp']=msg['bid_price']; self.df.at[s,'as']=msg['ask_size']; self.df.at[s,'ap']=msg['ask_price']
                    else:
                        self.df.at[s, 's']  = 0
                        self.df.at[s, 'bs'] = 0; self.df.at[s,'bp']=0; self.df.at[s,'as']=0; self.df.at[s,'ap']=0   ## indices are 0

                elif msg["data"] in ('conn','other','subscribe','unsubscribe'):
                    if msg['code']==200: print(f"{self.clsNm} msg: {msg['message']}")
                    else:                print(f"{self.clsNm} msg: code={msg['code']} {msg['message']}")
                
                else: print( msg )

            else:   print( f'{self.clsNm} msg_unkown:', msg )            
            #t2=time.perf_counter(); print(f'on_msg: {t2-t1}')       ##2500 call/s or max 0.0004 per call
        
        except Exception as e:
            
            if msg['symbol'] not in self.df.index:
                print(f'{self.clsNm} msg ex: {msg['symbol']} not in DF')
                self.addSym( msg['symbol'])
            
            else:   print(f'{self.clsNm} msg ex: {msg['symbol']} {e}')

            return 0

    
    def printDF(self):
        '''Debug and print few fields of a specific symbol'''

        global cdt, printDFlist
        try:
            if len(printDFlist) < 1: return 0

            d = self.df.query(f't == {candle(cdt)} and c != wl and (v != wv or v == 0) and n in {printDFlist}')[['n','t','c','v']]
            
            if d.empty:     return 0
            else: print(d); return 1
        
        except Exception as e:
            print(f'{self.clsNm} print(): {e}')
            return 0


    def writeDF(self):
        '''Snapshot the DF here and send RTD to socket'''

        rcdt()
        #;t1=time.perf_counter()
        
        global cdt      #, outData
        try:
               # {t}and c != wl and (v != wv or v == 0)     # vol_chg OR ltp_chg, less strict
            d = self.df.query(f't == {candle(cdt)} and (v != wv or (c != wl and v == 0))')
            
            if d.empty: return 0
            
            j = d[self.outcols].to_json( orient="records" )
        
            ## Log messages to file
            #d.to_csv( outData, columns=['n', 'd', 't', 'o', 'h', 'l', 'c', 'v', 'oi'], index=False, header=False, mode='w')
            
            self.df['wl'] = self.df['c'];   self.df['wv'] = self.df['v'] ##ok on FULL df, use assign() and operating on slice throws issues.
            
            #t2=time.perf_counter(); print(f'writeDF: {t2-t1}')         ## performance timer
            
            return  j       ## JSON in WS mode,    #return 1 ## in AB.Import mode
        except Exception as e:
            print(f'{self.clsNm} writeDF(): {e}')
            return 0

    ###  Below 3 Debugging functions ###
    
    def printCurrList(self):    print(f"{self.clsNm} current list: {', '.join( self.symbols ) }"); return 0


    def funcPrintMsg(self):
        if self.printMsgsF: self.printMsgsF = False
        else:               self.printMsgsF = True
        return 0            ## Debug func to set Flag to print WS msgs to stdio.
    

    def funcDebugSym(self, a):
        if a in self.symbols:   self.debugSym = a
        else:                   self.debugSym = None



#######  USAGE  ######

## some symbols
symbs           = [ 'SYM1', 'SYM2', 'SYM3', 'SYM4', 'SYM5' ]

## instantiate data class
vendor_ws_1     = VendorDataSocket( symbols=symbs )

## start data socket
vendor_ws_1.connect()


### other usages ###

## loop this to push data, like in client.py
vendor_ws_1.writeDF()

## Unsubscribe and Subscribe
vendor_ws_1.unsubscribe_symbol( [ 'SYM2', 'SYM4'] )

vendor_ws_1.subscribe_symbol( [ 'SYM6', 'SYM7' ] )


## 3 various debug functions
vendor_ws_1.printDF()


## disconnect socket
vendor_ws_1.disconnect()