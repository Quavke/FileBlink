import aiohttp
import asyncio
from fastapi import UploadFile
from src.config import VT_API

# TODO обработка файлов больше чем 32мб


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
