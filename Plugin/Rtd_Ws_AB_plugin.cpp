#include "aflplugin.h"
#include <windows.h>
#include <stdio.h>
#include <string>

// Plugin Info structure
PluginInfo pluginInfo = {
    sizeof(PluginInfo),
    "WsRtd Feed",         // Plugin name
    "1.0",                // Version
    "Rishi",              // Author
    PLUGIN_TYPE_REALTIME  // Plugin type
};

// Pipe handle
HANDLE hPipe = NULL;

// Amibroker calls this to get plugin info
PLUGINAPI int __cdecl GetPluginInfo(PluginInfo* pInfo) {
    if (!pInfo) return 0;
    *pInfo = pluginInfo;
    return 1;
}

// Init when plugin loads
PLUGINAPI int __cdecl Init() {
    return 1;
}

// Cleanup
PLUGINAPI int __cdecl Release() {
    if (hPipe) {
        CloseHandle(hPipe);
        hPipe = NULL;
    }
    return 1;
}

// Helper to read one tick JSON
bool ReadTick(char* symbolBuf, double* priceBuf) {
    if (!hPipe || hPipe == INVALID_HANDLE_VALUE) {
        hPipe = CreateFileA(
            R"(\\.\pipe\AbFeedPipe)",
            GENERIC_READ,
            0, NULL, OPEN_EXISTING, 0, NULL
        );
        if (hPipe == INVALID_HANDLE_VALUE) return false;
    }

    char buffer[512] = {0};
    DWORD bytesRead = 0;
    BOOL success = ReadFile(hPipe, buffer, sizeof(buffer) - 1, &bytesRead, NULL);
    if (!success || bytesRead == 0) {
        CloseHandle(hPipe);
        hPipe = NULL;
        return false;
    }

    std::string line(buffer);
    size_t s1 = line.find("\"symbol\":\"");
    size_t s2 = line.find("\"lp\":");

    if (s1 == std::string::npos || s2 == std::string::npos) return false;

    s1 += 10;
    size_t end1 = line.find("\"", s1);
    std::string symbol = line.substr(s1, end1 - s1);

    s2 += 5;
    size_t end2 = line.find("}", s2);
    std::string price = line.substr(s2, end2 - s2);

    strncpy(symbolBuf, symbol.c_str(), 63);
    *priceBuf = atof(price.c_str());
    return true;
}

// Amibroker asks for real-time quote
PLUGINAPI int __cdecl RTData(short command, const char* ticker, void* buffer) {
    if (command == RTPLUGIN_GETQUOTE) {
        static char lastSymbol[64] = "";
        static double lastPrice = 0;

        char newSymbol[64] = "";
        double newPrice = 0;

        if (ReadTick(newSymbol, &newPrice)) {
            strncpy(lastSymbol, newSymbol, 63);
            lastPrice = newPrice;
        }

        if (_stricmp(lastSymbol, ticker) == 0) {
            *((double*)buffer) = lastPrice;
            return 1;
        }
    }
    return 0;
}
