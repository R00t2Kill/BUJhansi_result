import requests
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from PyPDF2 import PdfMerger
import time
def func(rollno_from=231381030001,rollno_to=231381030067,ddlCourse="1030203",course_name=None,result_type=""):

    os.makedirs(f"./{course_name}_results", exist_ok=True)


    # Target URL
    url = "https://exam.bujhansi.ac.in/frmViewCampusCurrentResult.aspx?cd=MwA3ADkA"

    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Referer": url,
    }   

    session=requests.Session()

    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    if os.path.exists("./src_page"):
        with open("./src_page","r") as fobj:
            response_text=fobj.read()
    else:
        page=session.get(url,headers=headers,timeout=10)
        response_text=page.text
        with open("./src_page","w") as fobj:
            fobj.write(response_text)

    soup = BeautifulSoup(response_text, 'html.parser')

    # Extract hidden fields
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"] if soup.find("input", {"name": "__VIEWSTATE"}) else ""
    viewstategen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"] if soup.find("input", {"name": "__VIEWSTATEGENERATOR"}) else ""
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"] if soup.find("input", {"name": "__EVENTVALIDATION"}) else ""


    # Define CSS to fix page cutoff issue
    css = CSS(string="""
        @page {
            size: 260mm 297mm;  /* Slightly wider than A4 */
            margin: 10mm;
        }

        html, body {
            font-size: 9px;
            margin: 0;
            padding: 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            table-layout: auto; /* allow flexible sizing */
            page-break-inside: avoid;
        }

        td, th {
            border: 1px solid #000;
            padding: 2px;
            word-break: break-word;
            overflow-wrap: break-word;
            font-size: 8.5px;
        }

        tr {
            page-break-inside: avoid;
        }

        img {
            max-width: 100%;
            height: auto;
            display: block;
            page-break-inside: avoid;
        }
    """)








    for i in range(int(rollno_from),int(rollno_to)+1):

        # Form data
        payload = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategen,
            "__EVENTVALIDATION": eventvalidation,
            "txtUniqueID": i,
            "ddlCourse": ddlCourse,
            "ddlResultType": result_type,
            "btnGetResult": "View Result",
        }

        # Step 2: Submit form

        response = session.post(url, headers=headers, data=payload,timeout=10)
        time.sleep(1)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        #check if response is valid result
        if soup.find(string='NAME OF FATHER'):
            # Find all image tags
            for img_tag in soup.find_all("img"):
                if "src" in img_tag.attrs:
                    img_url = img_tag["src"]
                    
                    # Convert relative URLs to absolute URLs
                    if not img_url.startswith("http"):
                        img_url = "https://exam.bujhansi.ac.in/" + img_url

                    # Download and convert to Base64
                    img_response = session.get(img_url,timeout=10)
                    img_base64 = base64.b64encode(img_response.content).decode()
                    img_format = img_response.headers["Content-Type"].split("/")[-1]  # Get image format

                    # Replace image src with base64 data
                    img_tag["src"] = f"data:image/{img_format};base64,{img_base64}"

            # Convert updated HTML to string
            html_content = str(soup)



            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(f"{course_name}_results/result_{i}.pdf",stylesheets=[css])

            print(f"PDF saved as result_{i}.pdf in results{course_name}")




    # Directory containing the downloaded PDFs



    pdf_directory = f"{course_name}_results/"


    # Get list of all PDFs in the directory, sorted in numerical order
    pdf_files = sorted(
        [f for f in os.listdir(pdf_directory) if f.endswith(".pdf")],
        key=lambda x: int(x.split("_")[1].split(".")[0])
    )

    # Initialize PDF Merger
    merger = PdfMerger()

    # Merge all PDFs
    for pdf in pdf_files:
        merger.append(os.path.join(pdf_directory, pdf))

    # Save the merged PDF
    output_pdf = f"{course_name}_merged_results.pdf"
    merger.write(output_pdf)
    merger.close()

    print(f"Merged PDF saved as {output_pdf}")

