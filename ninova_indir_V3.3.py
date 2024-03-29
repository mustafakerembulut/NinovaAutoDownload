###
kullanici_adi = None
sifre = None
###

import subprocess
import os
import getpass

try:
    import requests
except:
    print("!!!Requests kutuphanesi eksik.\nEksik kutuphane indiriliyor")
    subprocess.check_call(['pip', 'install', 'requests'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import requests
    print()

try:
    from bs4 import BeautifulSoup as bs
except:
    print("!!!BeautifulSoup kutuphanesi eksik.\nEksik kutuphane indiriliyor")
    subprocess.check_call(['pip', 'install', 'beautifulsoup4'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from bs4 import BeautifulSoup as bs
    print()

import re

class Ninova:
    def __init__(self, kadi, sifre):
        self.kadi = kadi
        self.sifre = sifre
        self.file_path = os.path.dirname(os.path.abspath(__file__))+"/"
        self.indirme_sayisi = 0
        self.file_types = [".jpg",".jpeg",".pdf",".docx",".mp4",".mp3",".avi",".exe",".txt",".doc",".xls",".xlsx",".rar",".zip",".csv",".html",".ppt",".pptx",".sh"]
        self.forbidden_chars = r'[<>:"/\\|?*]'
        self.kampus_url = "https://ninova.itu.edu.tr/Kampus1"
        self.req = requests.Session()
        try:
            r = self.req.get(self.kampus_url)
        except:
            print("\nNinova'ya baglanilamadi, lutfen internet baglantinizi kontrol ediniz")
            exit()
        bs_content = bs(r.content.decode("utf-8"), "html.parser")
        viewstate = bs_content.find("input", {"name":"__VIEWSTATE"})["value"]
        viewstategenerator = bs_content.find("input", {"name":"__VIEWSTATEGENERATOR"})["value"]
        eventvalidation = bs_content.find("input", {"name":"__EVENTVALIDATION"})["value"]
        login_data = {"__VIEWSTATE":viewstate,
                        "__VIEWSTATEGENERATOR":viewstategenerator,
                        "__EVENTVALIDATION":eventvalidation,
                        "ctl00$ContentPlaceHolder1$hfAppName":"Ninova",
                        "ctl00$ContentPlaceHolder1$tbUserName":kadi,
                        "ctl00$ContentPlaceHolder1$tbPassword":sifre,
                        "ctl00$ContentPlaceHolder1$btnLogin":"Giriş / Login"}
        r = self.req.post(r.url, login_data)
        if r.url[:26] == "https://ninova.itu.edu.tr/":
            print("Ninova'ya giris basarili")
        else:
            print("\n!!!Ninova'ya giris basarisiz!!!")
            print("Kullanici adi ya da sifre hatali olabilir, lutfen tekrar deneyiniz")
            exit()

    def get_classes(self):
        self.classes = [] 
        r = self.req.get(self.kampus_url)
        soup = bs(r.content.decode("utf-8"), 'html.parser')
        ul_element = soup.find('div', class_='menuErisimAgaci').find("ul")
        li_elements = ul_element.find_all('li', recursive=False)
        for li in li_elements:
            href = li.find("a").get("href")
            class_name = li.find("span").text
            self.classes.append([class_name, href])
    
    def makedir_classes(self):
        for c in self.classes:
            print()
            print("Sinif: ",c[0])
            current_path = c[0]
            isExist = os.path.exists(self.file_path+c[0])
            if not isExist:
                os.makedirs(self.file_path+c[0])
                print("Klasor olusturuldu:",c[0])

            ders_dosyalari = self.get_files("https://ninova.itu.edu.tr/"+c[1]+"/DersDosyalari")
            if len(ders_dosyalari)>0:
                isExist = os.path.exists(self.file_path+current_path+"/Ders Dosyalari")
                if not isExist:
                    os.makedirs(self.file_path+current_path+"/Ders Dosyalari")
                    print("Klasor olusturuldu:","Ders Dosyalari")
                ninova.makedir_download(ders_dosyalari, current_path+"/Ders Dosyalari")
            else:
                # print("Ders dosyalari bos, klasor olusturulmadi")
                pass

            sinif_dosyalari = self.get_files("https://ninova.itu.edu.tr/"+c[1]+"/SinifDosyalari")
            if len(sinif_dosyalari)>0:
                isExist = os.path.exists(self.file_path+current_path+"/Sinif Dosyalari")
                if not isExist:
                    os.makedirs(self.file_path+current_path+"/Sinif Dosyalari")
                    print("Klasor olusturuldu:","Sinif Dosyalari")
                ninova.makedir_download(sinif_dosyalari, current_path+"/Sinif Dosyalari")
            else:
                # print("Sinif dosyalari bos, klasor olusturulmadi")
                pass

            hw_files = self.get_hw_files("https://ninova.itu.edu.tr/"+c[1]+"/Odevler")
            if len(hw_files)>0:
                isExist = os.path.exists(self.file_path+current_path+"/Odevler")
                if not isExist:
                    os.makedirs(self.file_path+current_path+"/Odevler")
                    print("Klasor olusturuldu:","Odevler")
                ninova.makedir_hw_download(hw_files, current_path+"/Odevler")
            else:
                # print("Odev dosyalari bos, klasor olusturulmadi")
                pass
            print()
        
    def get_hw_files(self, url):
        r = self.req.get(url)
        folders = []
        #id="ctl00_ContentPlaceHolder1_gvOdevListesi"
        soup = bs(r.content.decode("utf-8"), 'html.parser')
        table_element = soup.find('table', id='ctl00_ContentPlaceHolder1_gvOdevListesi')
        tr_elements = table_element.find_all('tr')
        for tr in tr_elements:
            td_elements = tr.find_all('td')
            for td in td_elements:
                h2_elements = td.find_all('h2')
                for h2 in h2_elements:
                    a_elements = h2.find_all('a')
                    for a in a_elements:
                        href = a.get("href")
                        href = "https://ninova.itu.edu.tr/"+href
                        folder_name = a.get_text()
                        folder_name = re.sub(self.forbidden_chars, '_', folder_name)
                        folders.append([href, folder_name])

        #id="ctl00_ContentPlaceHolder1_gvDosyalar"
        files = []
        for folder in folders:
            r = self.req.get(folder[0])
            soup = bs(r.content.decode("utf-8"), 'html.parser')
            table_element = soup.find('table', id='ctl00_ContentPlaceHolder1_gvDosyalar')
            tr_elements = table_element.find_all('tr')
            for tr in tr_elements[1:]:
                td_elements = tr.find_all('td')
                for td in td_elements:
                    a_elements = td.find_all('a')
                    for a in a_elements:
                        href = a.get("href")
                        href = "https://ninova.itu.edu.tr"+href
                        text = a.get_text()
                        text = re.sub(self.forbidden_chars, '_', text)
                        files.append([href,folder[1], text])
        return files
    
    def makedir_hw_download(self, files, current_path):
        for file in files:

            folder_path = current_path+"/"+file[1]
            if not self.file_name_exists(file[1],current_path):
                os.makedirs(self.file_path+folder_path)
                print("Klasor olusturuldu:",file[1])

            if not self.file_name_exists(file[2],folder_path):
                file_type, url = self.get_file_type(file[0])
                
                if file_type == ".url":
                    self.indirme_sayisi += 1
                    print("Dosya indiriliyor:",file[2])
                    url = url
                    with open(self.file_path+folder_path+"/"+file[2], "w") as file:
                        file.write("[InternetShortcut]\n")
                        file.write(f"URL={url}\n")
                else:
                    if file_type == file[1][-len(file_type):]:
                        self.indirme_sayisi += 1
                        r = self.req.get(url)
                        print("Dosya indiriliyor:",file[2])
                        with open(self.file_path+folder_path+"/"+file[2], "wb") as file:
                            file.write(r.content)
                    else:
                        self.indirme_sayisi += 1
                        r = self.req.get(url)
                        print("Dosya indiriliyor:",file[2])
                        with open(self.file_path+folder_path+"/"+file[2], "wb") as file:
                            file.write(r.content)

    def get_files(self, url):
        c = 0
        files = []
        r = self.req.get(url)
        soup = bs(r.content.decode("utf-8"), 'html.parser')
        div_element = soup.find('div', class_='dosyaSistemi')
        tr_elements = div_element.find_all('tr')
        for tr in tr_elements[2:]:
            td_elements = tr.find_all('td')
            for td in td_elements:
                a_elements = td.find_all('a')
                for a in a_elements:
                    href = a.get("href")
                    href = "https://ninova.itu.edu.tr"+href
                    text = a.get_text()
                    text = re.sub(self.forbidden_chars, '_', text)
                    files.append([href, text])
        return files

    def makedir_download(self, files, current_path):
        for file in files:
            if not self.file_name_exists(file[1],current_path):
                file_type, url = self.get_file_type(file[0])
                if file_type == "folder":
                    folder_path = current_path+"/"+file[1]
                    os.makedirs(self.file_path+folder_path)
                    print("Klasor olusturuldu:",file[1])
                    files = self.get_files(url)
                    self.makedir_download(files, folder_path)
                elif file_type == ".url":
                    self.indirme_sayisi += 1
                    print("Dosya indiriliyor:",file[1]+file_type)
                    url = url
                    with open(self.file_path+current_path+"/"+file[1]+file_type, "w") as file:
                        file.write("[InternetShortcut]\n")
                        file.write(f"URL={url}\n")
                else:
                    if file_type == file[1][-len(file_type):]:
                        self.indirme_sayisi += 1
                        r = self.req.get(url)
                        print("Dosya indiriliyor:",file[1])
                        with open(self.file_path+current_path+"/"+file[1], "wb") as file:
                            file.write(r.content)
                    else:
                        self.indirme_sayisi += 1
                        r = self.req.get(url)
                        print("Dosya indiriliyor:",file[1]+file_type)
                        with open(self.file_path+current_path+"/"+file[1]+file_type, "wb") as file:
                            file.write(r.content)

    def get_file_type(self, url):
        r = self.req.head(url)
        content_disposition = r.headers.get("content-disposition")
        location = r.headers.get("Location")
        
        if content_disposition:
            ft = content_disposition[-5:]
            try:
                ft = ft.split(".")[1]
                file_type = "."+ft
            except:
                file_type = ""
                for typ in self.file_types:
                    if typ in content_disposition:
                        file_type = typ
                        break
                if file_type == "":
                    print()
                    print("HATA! Bilinmeyen dosya türü: ", content_disposition.split("filename=")[1])
                    print("Dosya türü boş olarak seçildi")
                    print()
        elif location:
            url = location
            for i in range(10):
                try:
                    r = self.req.head(url, allow_redirects=True)
                except:
                    break
                if r.history:
                    url = r.url
                else:
                    break
            file_type = ".url"
        else:
            file_type = "folder"

        return file_type, url

    def file_name_exists(self,file_name, directory='.'):
        for file in os.listdir(self.file_path+directory):
            base, ext = os.path.splitext(file)
            if file == file_name or base == file_name:
                return True
        return False
    
    def save_user_data(self):
        file_name = os.path.basename(__file__)
        file_path = self.file_path+file_name
        with open(file_path, "r") as file:
            code = file.read()
        code = code.replace("kullanici_adi = None", f"kullanici_adi = '{kullanici_adi}'",1)
        code = code.replace("sifre = None", f"sifre = '{sifre}'",1)
        
        with open(file_name, "w") as file:
            file.write(code)

    def main(self):
        self.get_classes()
        self.makedir_classes()
        if self.indirme_sayisi == 0:
            print("Dosyalariniz tam, indirme yapilmadi")
        else:
            print()
            print("Indirilen dosya sayisi:", self.indirme_sayisi)


if __name__ == "__main__":
    if kullanici_adi is None or sifre is None:
        kullanici_adi = input("Kullanici adinizi girin: ")
        sifre = getpass.getpass("Sifrenizi girin: ")
        save_input = input("Kullanici adi ve sifre kaydedilsin mi? (Y/N): ").upper()

    ninova = Ninova(kullanici_adi, sifre)
    try:
        if save_input == "Y":
            ninova.save_user_data()
    except:
        pass
    ninova.main()
