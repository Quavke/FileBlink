# import os
# from src.config import VT_API
# import aiohttp


# async def vt_check_func(file):
#     params = {"apikey": VT_API}
#     url = "https://www.virustotal.com/vtapi/v2/file/scan"
#     async with aiohttp.ClientSession() as session:
#         file_content = await file.read()
#         data = aiohttp.FormData()
#         data.add_field('file', file_content, filename=file.filename)
#         async with session.post(url, data=data, params=params) as response:
#             json_response = await response.json()
#     # Получаем отчет о сканировании файла
#     report_url = "https://www.virustotal.com/vtapi/v2/file/report"
#     params = {"apikey": VT_API, "resource": json_response["resource"]}
#     async with aiohttp.ClientSession() as session:
#         async with session.get(report_url, params=params) as report_response:
#             try:
#                 report_data = await report_response.json()
#             except Exception:
#                 return {"error": "unexpected mimetype:",
#                         "status": "error",
#                         "message": "try again"}
#     m_count = 0
#     for value in report_data['scans'].values():
#         try:
#             if value['detected'] is True:
#                 m_count += 1
#         except Exception as e:
#             return {"error": str(e),
#                     "status": "error",
#                     "message": "try again"}
#     return m_count

# import io
# import zipfile
# from typing import Optional
# from fastapi import UploadFile
# from src.config import VT_API
# import aiohttp
# import asyncio


# async def vt_check_func(file: UploadFile):
#     url_scan = "https://www.virustotal.com/api/v3/files"
#     headers = {
#         "x-apikey": VT_API
#     }

#     async with aiohttp.ClientSession() as session:
#         print("1")
#         await file.seek(0)
#         file_data = await file.read()
#         # file_content = await file.read()
#         file_io = io.BytesIO(file_data)
#         data = aiohttp.FormData()
#         # Сначала проверим, является ли файл zip-архивом и защищен ли он паролем
#         # if await is_zipfile(file):
#         #     password_check = await check_zip_password(file)
#         #     if password_check.get("is_password_protected"):
#         #         if password:
#         #             data.add_field('password', password)
#         #         else:
#         #             return {"error": "Password protected zip file", "status": "error",
#         #                     "message": "Password required for the zip file"}

#         # Подготовка данных для отправки

#         data.add_field('file', file_io, filename=file.filename,
#                        content_type='application/octet-stream')
#         print("2")
#         # Отправка файла на сканирование
#         async with session.post(url_scan, headers=headers, data=data) as response:
#             if response.status != 200:
#                 return {"error": f"Failed to scan file: {response.status}", "status": "error"}
#             scan_result = await response.json()
#             analysis_id = scan_result['data']['id']
#             print("3")
#         # Ожидаем завершения анализа
#         url_analysis = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
#         print("while start")
#         while True:
#             async with session.get(url_analysis, headers=headers) as analysis_response:
#                 if analysis_response.status != 200:
#                     print("if analysis_response.status != 200")
#                     return {"error": f"Failed to get analysis: {analysis_response.status}", "status": "error"}

#                 analysis_result = await analysis_response.json()
#                 if analysis_result['data']['attributes']['status'] == 'completed':
#                     print("analysis_result['data']['attributes']['status']")
#                     sha256 = analysis_result['meta']['file_info']['sha256']
#                     print("while close")
#                     break

#                 # Ждем 10 секунд перед повторной проверкой
#                 await asyncio.sleep(25)
#         print("4")
#         # Получение отчета о файле
#         url_file_report = f"https://www.virustotal.com/api/v3/files/{sha256}"
#         async with session.get(url_file_report, headers=headers) as report_response:
#             if report_response.status != 200:
#                 return {"error": f"Failed to get file report: {report_response.status}", "status": "error"}
#             file_report = await report_response.json()
#             print("5")
#         # Подсчет количества обнаруженных угроз
#         m_count = sum(1 for scan in file_report['data']['attributes']['last_analysis_results'].values() if
#                       scan['category'] == 'malicious')

#         # m_count = file_report['data']['attributes']['total_votes']['malicious']

#         return m_count

import aiohttp
import asyncio
from fastapi import UploadFile
from src.config import VT_API


async def vt_check_func(file: UploadFile):
    url_scan = "https://www.virustotal.com/api/v3/files"
    headers = {
        "x-apikey": VT_API
    }

    async with aiohttp.ClientSession() as session:
        # Prepare file data for upload
        data = aiohttp.FormData()
        file_content = await file.read()
        data.add_field('file', file_content, filename=file.filename,
                       content_type='application/octet-stream')

        # Send file for scanning
        async with session.post(url_scan, headers=headers, data=data) as response:
            if response.status != 200:
                response_text = await response.text()
                return {"error": f"Failed to scan file: {response.status}", "status": "error", "details": response_text}
            scan_result = await response.json()
            analysis_id = scan_result['data']['id']

        # Wait for analysis to complete
        url_analysis = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        while True:
            # print("while start")
            async with session.get(url_analysis, headers=headers) as analysis_response:
                if analysis_response.status != 200:
                    response_text = await analysis_response.text()
                    # print("error")
                    return {"error": f"Failed to get analysis: {analysis_response.status}", "status": "error", "details": response_text}

                analysis_result = await analysis_response.json()
                if analysis_result['data']['attributes']['status'] == 'completed':
                    sha256 = analysis_result['meta']['file_info']['sha256']
                    # print("while end")
                    break
                await asyncio.sleep(60)

        # Get file report
        url_file_report = f"https://www.virustotal.com/api/v3/files/{sha256}"
        async with session.get(url_file_report, headers=headers) as report_response:
            if report_response.status != 200:
                response_text = await report_response.text()
                return {"error": f"Failed to get file report: {report_response.status}", "status": "error", "details": response_text}
            file_report = await report_response.json()

        # Count malicious detections
        m_count = sum(1 for scan in file_report['data']['attributes']['last_analysis_results'].values() if
                      scan['category'] == 'malicious')

        return m_count
