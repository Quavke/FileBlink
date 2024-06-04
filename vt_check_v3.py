import io
import zipfile
from typing import Optional
from fastapi import UploadFile
from src.config import VT_API
import aiohttp
import asyncio


async def vt_check_func(file: UploadFile):
    url_scan = "https://www.virustotal.com/api/v3/files"
    headers = {
        "x-apikey": VT_API
    }

    async with aiohttp.ClientSession() as session:
        print("1")
        await file.seek(0)
        file_data = await file.read()
        # file_content = await file.read()
        file_io = io.BytesIO(file_data)
        data = aiohttp.FormData()
        # Сначала проверим, является ли файл zip-архивом и защищен ли он паролем
        # if await is_zipfile(file):
        #     password_check = await check_zip_password(file)
        #     if password_check.get("is_password_protected"):
        #         if password:
        #             data.add_field('password', password)
        #         else:
        #             return {"error": "Password protected zip file", "status": "error",
        #                     "message": "Password required for the zip file"}

        # Подготовка данных для отправки

        data.add_field('file', file_io, filename=file.filename,
                       content_type='application/octet-stream')
        print("2")
        # Отправка файла на сканирование
        async with session.post(url_scan, headers=headers, data=data) as response:
            if response.status != 200:
                return {"error": f"Failed to scan file: {response.status}", "status": "error"}
            scan_result = await response.json()
            analysis_id = scan_result['data']['id']
            print("3")
        # Ожидаем завершения анализа
        url_analysis = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        print("while start")
        while True:
            async with session.get(url_analysis, headers=headers) as analysis_response:
                if analysis_response.status != 200:
                    print("if analysis_response.status != 200")
                    return {"error": f"Failed to get analysis: {analysis_response.status}", "status": "error"}

                analysis_result = await analysis_response.json()
                if analysis_result['data']['attributes']['status'] == 'completed':
                    print("analysis_result['data']['attributes']['status']")
                    sha256 = analysis_result['meta']['file_info']['sha256']
                    print("while close")
                    break

                # Ждем 10 секунд перед повторной проверкой
                await asyncio.sleep(25)
        print("4")
        # Получение отчета о файле
        url_file_report = f"https://www.virustotal.com/api/v3/files/{sha256}"
        async with session.get(url_file_report, headers=headers) as report_response:
            if report_response.status != 200:
                return {"error": f"Failed to get file report: {report_response.status}", "status": "error"}
            file_report = await report_response.json()
            print("5")
        # Подсчет количества обнаруженных угроз
        m_count = sum(1 for scan in file_report['data']['attributes']['last_analysis_results'].values() if
                      scan['category'] == 'malicious')

        # m_count = file_report['data']['attributes']['total_votes']['malicious']

        return m_count
