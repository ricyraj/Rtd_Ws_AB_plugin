// Rtd_Ws_AB_plugin.cpp

#include <windows.h>
#include "aflplugin.h"

// Plugin Info Function (Amibroker uses this)
extern "C" __declspec(dllexport)
PLUGININFO* GetPluginInfo()
{
    static PLUGININFO pluginInfo = {
        sizeof(PLUGININFO),
        "WsRTD Plugin",     // Name shown in AmiBroker
        "1.0",              // Version
        "OpenAI GPT Plugin" // Author
    };
    return &pluginInfo;
}

// Dummy RTD thread (AmiBroker calls this when plugin is loaded)
extern "C" __declspec(dllexport)
DWORD WINAPI RTDServerThread(LPVOID lpParameter)
{
    // Example: just sleep forever (actual pipe reading code will go here)
    while (true)
    {
        Sleep(1000);  // Idle loop
    }
    return 0;
}
