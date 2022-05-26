from enum import Flag
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urlparse

class Crawler:

    def __init__(self, url, auth_url, user, password):
        self.url = url
        self.auth_url = auth_url
        self.user = user
        self.password = password
        self.base_url = urlparse(url).netloc
        self.urls = []
        self.domain_urls = []
        self.protected_urls = []
        self.urls_404 = []
        self.urls_externe = []
        self.urls_with_forms = []
        self.is_crawl = False
        self.is_auth = False
        self.crawl()
            
    def get_page(self, url):
        if urlparse(url).netloc == self.base_url:
            try:
                session = HTMLSession()
                if self.user is not None and self.password is not None and self.is_auth == False:
                        authResponse = session.post(self.auth_url, auth=(self.user, self.password))
                        if authResponse.status_code == 200:
                            print('Authentification réussi')
                            self.is_auth = True
                print("Récupération de la page {}".format(url))
                page = session.get(url)
                # On force le rendu de la page pour charger tout les éléments dynamiques
                page.html.render()
                if page.status_code == 404:
                    self.urls_404.append(url)
                # On filtre sur les codes http 401 (unauthorized) et 302 (redirect) pour les pages protégés
                if page.status_code == 401 or page.status_code == 302:
                    self.protected_urls.append(url)
                return page.text
            except:
                print("Impossible de récupérer la page {}".format(url))
        else:
            print("l'URL externe {} ne sera pas analysée.".format(url))
            if url not in self.urls_externe:
                self.urls_externe.append(url)

    def retrieve_links(self, page):
        """
            Analyse la page et retourne toutes les URL's présentes dans les liens :
                - Ajoute les URL's à la liste self.urls si elle n'est pas présente dans url's visitees        
        """
        soup = BeautifulSoup(page, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            if not link['href'].startswith('#'):
                # Si le lien commence par un # alors c'est une ancre et on peut l'ignorer
                if link['href'].startswith('/'):
                    # On retire le premier '/' avant la concaténation
                    link['href'] = link['href'][1:]
                    # On reconstruit l'URL
                    link['href'] = self.url + link['href']
                    if link['href'] not in self.urls and urlparse(link['href']).netloc == self.base_url:
                        self.urls.append(link['href'])
                        self.domain_urls.append(link['href'])
                elif link['href'].startswith('http') and link['href'] not in self.urls:
                    self.urls.append(link['href'])
                    if urlparse(link['href']).netloc == self.base_url: 
                        self.domain_urls.append(link['href'])

    def retrieve_forms(self, page, url):
        """
            Analyse la page et retourne toutes les URL's contenant des formulaires:
                - Ajoute les URL's à la liste self.urls_with_forms    
        """
        soup = BeautifulSoup(page, 'html.parser')
        if url == "https://etik.tech//nous-contacter":
            with open("test.html", 'w', encoding="utf-8") as f:
                f.write(str(soup))
        forms = soup.find_all("form")
        for form in forms:
            self.urls_with_forms.append(url)
  
    def nombre_url(self):
        """
            Retourne le nombre de pages trouvées
        """
        return len(self.urls)
    
    def export(self, file): 
        """
            Exporte un rapport dans un fichier donné
        """
        with open(file + ".txt", 'w', encoding="utf-8") as f:
            # On ajoute au fichier le nombre d'urls uniques
            f.write("Nombre d'URL uniques: {}".format(len(self.urls)))
            f.write('\n')
            # On ajoute au fichier les urls pointant sur le même domaine
            f.write("URL's pointant sur le même domaine: ")
            f.write('\n')
            for url in self.domain_urls:
                f.write("\t- {}".format(url))
                f.write('\n')
            # On ajoute au fichier les urls pointant sur un domaine externe
            f.write("URL's pointant sur un domaine externe: ")
            f.write('\n')
            for url in self.urls_externe:
                f.write("\t- {}".format(url))
                f.write('\n')
            # On ajoute au fichier les urls contenant des formulaires
            f.write("URL's contenant des formulaires: ")
            f.write('\n')
            for url in self.urls_with_forms:
                f.write("\t- {}".format(url))
                f.write('\n')
            # On ajoute au fichier les urls protégés par mot de passe
            f.write("URL's protégés par mot de passe: ")
            f.write('\n')
            for url in self.protected_urls:
                f.write("\t -{}".format(url))
                f.write('\n')
            f.write("Nombre d'adresses pointant sur le même nom de domaine renvoyant une page 404: {}".format(len(self.urls_404)))
            f.write('\n')

    def print_urls(self): 
        """
            Retourne un rapport dans le terminal
        """
        print(self.urls)
    
    def list_404(self):
        """
            Renvoit la liste de toutes les pages en 404
        """
        if len(self.urls_404) > 0:
            print("Liste des pages en 404 : \n")
            for url_404 in self.urls_404:
                print("\t - {}".format(url_404))
        else:
            print("Aucune page d'erreur 404 n'a été trouvée")

    def list_protected(self):
        """
            Renvoit la liste de toutes les pages protégées
        """
        if len(self.protected_urls) > 0:
            print("Liste des pages protégées : \n")
            for url_protected in self.protected_urls:
                print("\t - {}".format(url_protected))
        else:
            print("Aucune page protégée par mot de passe n'a été trouvée")
    
    def list_url_externe(self):
        """
            Renvoit la liste des URL's externes
        """
        if self.is_crawl:
            if len(self.urls_externe) > 0:
                print("Liste des pages externes : \n")
                for url_externe in self.urls_externe:
                    print("\t - {}".format(url_externe))
            else:
                print("Aucune URL externe n'a été trouvée")
        else:
            print("Le site web n'a pas encore été analysé.")

    def crawl(self):
        # Premier appel sur self.url
        html = self.get_page(self.url)
        self.retrieve_links(html)
        self.retrieve_forms(html, self.url)

        # On itère sur la liste self.urls
        for url in self.urls:
            page = self.get_page(url)
            if page:
                self.retrieve_links(page)
                self.retrieve_forms(page, url)
        self.is_crawl = True
