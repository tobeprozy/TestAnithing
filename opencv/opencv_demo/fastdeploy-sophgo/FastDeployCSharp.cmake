list(APPEND FASTDEPLOY_DOTNET_REFERENCES
    "Microsoft.CSharp"
    "System"
    "System.Core"
    "System.Data"
    "System.Deployment"
    "System.Drawing"
    "System.Net.Http"
    "System.Xml"
    "System.Reflection"
    "${CMAKE_CURRENT_LIST_DIR}/csharp_lib/fastdeploy_csharp.dll")

set(FASTDEPLOY_PACKAGE_REFERENCES "OpenCvSharp4_4.7.0.20230115;OpenCvSharp4.runtime.win_4.7.0.20230115")
