@echo off

pushd "%~dp0\..\..\"

"%~dp0\nssm.exe" remove  ZoeClientService confirm
"%~dp0\nssm.exe" install ZoeClientService "%CD%\run.bat"
"%~dp0\nssm.exe" set     ZoeClientService Type SERVICE_INTERACTIVE_PROCESS
"%~dp0\nssm.exe" set     ZoeClientService AppStdout "%CD%\service-stdout.log.txt"
"%~dp0\nssm.exe" set     ZoeClientService AppStderr "%CD%\service-stderr.log.txt"
"%~dp0\nssm.exe" set     AppRestartDelay  10000
"%~dp0\nssm.exe" set     AppThrottle      10000
"%~dp0\nssm.exe" set     ZoeClientService AppRotateFiles 1
"%~dp0\nssm.exe" set     ZoeClientService AppRotateOnline 1
"%~dp0\nssm.exe" set     ZoeClientService AppRotateSeconds 0
"%~dp0\nssm.exe" set     ZoeClientService AppRotateBytes 50000
"%~dp0\nssm.exe" set     ZoeClientService AppEnvironmentExtra RUNNING_AS_WINDOWS_SERVICE=1
"%~dp0\nssm.exe" start   ZoeClientService SERVICE_AUTO_START
:: to set more options use 'edit:
::"%~dp0\nssm.exe" edit    ZoeClientService

popd

@pause