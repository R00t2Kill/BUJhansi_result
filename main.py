import requests
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS
import base64

import os
from PyPDF2 import PdfMerger
def func(rollno=231381030001,ddlCourse="1030203",result_type=""):
    # Target URL
    url = "https://exam.bujhansi.ac.in/frmViewCampusCurrentResult.aspx?cd=MwA3ADkA"

    # Headers
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
        "Referer": url,
    }

    # Start session
    session = requests.Session()

    # Step 1: Get hidden fields
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract hidden fields
    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"] if soup.find("input", {"name": "__VIEWSTATE"}) else ""
    viewstategen = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"] if soup.find("input", {"name": "__VIEWSTATEGENERATOR"}) else ""
    eventvalidation = soup.find("input", {"name": "__EVENTVALIDATION"})["value"] if soup.find("input", {"name": "__EVENTVALIDATION"}) else ""


    # Define CSS to fix page cutoff issue
    css = CSS(string="""
        @page { 
            size: A4 landscape; /* Set wider page size */
            margin: 20px; 
        }
        body { 
            word-wrap: break-word;
            overflow-wrap: break-word; 
            font-size: 12px;
        }
        img { 
            max-width: 100%; 
            display: block; 
            margin: 10px auto; 
        }
        table { 
            width: 100%; 
            border-collapse: collapse;
        }
        td, th { 
            padding: 5px; 
            border: 1px solid #ddd; 
        }
    """)

    for i in range(rollno,rollno+67):
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
        response = session.post(url, headers=headers, data=payload)
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
                    img_response = session.get(img_url)
                    img_base64 = base64.b64encode(img_response.content).decode()
                    img_format = img_response.headers["Content-Type"].split("/")[-1]  # Get image format

                    # Replace image src with base64 data
                    img_tag["src"] = f"data:image/{img_format};base64,{img_base64}"

            # Convert updated HTML to string
            html_content = str(soup)



            # Convert HTML to PDF
            HTML(string=html_content).write_pdf(f"results/result_{i}.pdf", stylesheets=[css])

            print(f"PDF saved as result_{i}.pdf")




    # Directory containing the downloaded PDFs
    pdf_directory = "results/"

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
    output_pdf = "merged_results.pdf"
    merger.write(output_pdf)
    merger.close()

    print(f"Merged PDF saved as {output_pdf}")

rollno=input("Plz enter a valid roll no.(the starting one): ")
ddlCourse=input("Plz enter the corresponding CourseID: ")
result_type=input("Enter 6 for special back(otherwise leave empty): ")
if rollno and ddlCourse or result_type:
    func(rollno,ddlCourse,result_type)
else:
    func()