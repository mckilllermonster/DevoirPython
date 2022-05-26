from crawler import Crawler
import click

@click.command()
@click.option('--url', '-u', required=True, help="Url à analyser")
@click.option('--export', '-e', help='Exporter le rapport dans un fichier donné')
@click.option('--not-found', '-nf', is_flag=True, help='Retourner uniquement les pages retournant un code erreur 404')
@click.option('--external-url', '-eu', is_flag=True, help='Retourner uniquement les adresses pointant vers un nom de domaine externe')
@click.option('--protected_url', '-pu', is_flag=True, help='Retourner uniquement les pages nécessitant une authentification')
@click.option('--auth-url', help='Url sur la quelle effectuer l\'authentification')
@click.option('--user', help='Paramètre user essayant de remplir automatiquement les champs de connexion')
@click.option('--password', help='Paramètre password essayant de remplir automatiquement les champs de connexion')

def cli(url, export, not_found, external_url, protected_url, auth_url, user, password):
    if auth_url is not None and user is not None and password is not None: 
        crawler = Crawler(url, auth_url, user, password)
    else:
        crawler = Crawler(url, None, None, None)
    if not_found != False: {
        crawler.list_404()
    } 
    elif external_url != False:
        crawler.list_url_externe()
    elif protected_url != False:
        crawler.list_protected()
    elif export != None:
        crawler.export(export)
    else: 
        crawler.print_urls()
    
if __name__ == '__main__':
    cli()
