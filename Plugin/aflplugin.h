#ifndef __AFLPLUGIN_H_
#define __AFLPLUGIN_H_

#ifndef PLUGINAPI
#define PLUGINAPI extern "C" __declspec(dllexport)
#endif

// plugin info structure
typedef struct _PluginInfo
{
    unsigned int cbSize;      // sizeof(PluginInfo)
    const char* szName;       // plugin name
    const char* szVersion;    // plugin version
    const char* szAuthor;     // author name
    int nType;                // plugin type
} PluginInfo;

// plugin type values
#define PLUGIN_TYPE_TOOL     0
#define PLUGIN_TYPE_DATA     1
#define PLUGIN_TYPE_REALTIME 2
#define PLUGIN_TYPE_DLL      3

// RT plugin constants
#define RTPLUGIN_GETTICKER    0x1000
#define RTPLUGIN_SETTICKER    0x1001
#define RTPLUGIN_ISCONNECTED  0x1002
#define RTPLUGIN_LOGIN        0x1003
#define RTPLUGIN_LOGOUT       0x1004
#define RTPLUGIN_REFRESH      0x1005
#define RTPLUGIN_GETQUOTE     0x1006
#define RTPLUGIN_GETVOLUME    0x1007
#define RTPLUGIN_GETOPENINT   0x1008
#define RTPLUGIN_GETTRADETIME 0x1009

// plugin API
PLUGINAPI int __cdecl GetPluginInfo(PluginInfo* pInfo);
PLUGINAPI int __cdecl Init();
PLUGINAPI int __cdecl Release();

#endif // __AFLPLUGIN_H_
