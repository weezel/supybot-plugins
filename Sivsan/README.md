# Hae sivistyssanoja ja niiden merkityksiä

## Riippuvuudet

* Python 2.7 tai uudempi
* Supybot (daa!)
* py-lxml
* py-cssselector

## Käyttö
Ohjeita saa komentamalla `@sivsan`.

Haetaan esimerkiksi sanat, jotka alkavat 'à' merkillä:

	@sivsan à*

Tai `ä` kirjaimeen loppuvat sivistyssanat:

	@sivsan *ä

## TODO

- [ ] Päivitä kanta automaattisesti netistä, kun edellisestä kerrasta on
  tarpeeksi pitkä aika.
