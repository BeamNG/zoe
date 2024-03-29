@echo off

"%~dp0\nssm.exe" stop ZoeClientService
"%~dp0\nssm.exe" remove ZoeClientService confirm

@pause