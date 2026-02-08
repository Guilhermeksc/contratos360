REadme 

bizu deletar tabelas

docker compose down
rm -rf postgres_data
docker compose up -d --build

docker exec -it postgres_licitacao psql -U postgres -d appdb

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

docker compose restart backend

ng build --configuration production


Sua chave de acesso para o e-mail "guilhermekscampos@gmail.com" é: 60d95214ce10336130ff2cdcb166c3a2

A chave de acesso é de uso pessoal, intransferível e de conhecimento exclusivo. É da inteira responsabilidade do usuário todo e qualquer prejuízo causado pelo fornecimento de sua chave pessoal a terceiros.

O acesso às API's deverá ser feito passando os seguintes dados no header da requisição:

            "[{"key":"chave-api-dados","value":"60d95214ce10336130ff2cdcb166c3a2"}]
        

scp /home/guilherme/Projetos/gerata/backend_worker/pncp.db \
root@72.60.52.231:~/contratos360/backend/django_licitacao360/apps/pncp/fixtures/


<script type="text/javascript" language="javascript">

function enviar()

{

	var requisicao = new XMLHttpRequest();	

	requisicao.addEventListener("load", listener);

	requisicao.open("GET", "http://api.portaldatransparencia.gov.br/api-de-dados/orgaos-siafi?pagina=1");	

	requisicao.setRequestHeader("chave-api-dados", "1d5r8yt963h2v4g5h6j3k138sbfiec21");

	requisicao.send();       

}


function listener() {

  alert(this.responseText);

}

</script>

<html>

    <body id='bod'>

        <button type="submit" onclick="javascript:enviar()">call</button>

        <div id='div'></div>

    </body>

</html>


https://portaldatransparencia.gov.br/download-de-dados/emendas-parlamentares

https://portaldatransparencia.gov.br/download-de-dados/ceis/20260105