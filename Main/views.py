from Genetic.selection import tournamentSelect,getRouletteWheel,rouletteWheelSelect,Individual
from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,DetailView,ListView
from .forms import FormularzPoczatkowy
from  .models import Epoka,PojedynczaWartoscWyniku,Ustawienia,Wynik
from django.contrib import messages
from django.utils import timezone
import statistics,math,random
import heapq



# Create your views here.



class MainView(TemplateView):
    def get(self, request, *args, **kwargs):
        formularz=FormularzPoczatkowy()
        contex={
            'formularz':formularz
        }
        return render(self.request, "Strona_glowna.html",contex)
    def post(self,*args,**kwargs):
        formularz = FormularzPoczatkowy(self.request.POST or None)
        if formularz.is_valid():
                zakres1 = formularz.cleaned_data.get('zakres1')
                zakres2 = formularz.cleaned_data.get('zakres2')
                dokladnosc_reprezentacji_chromsomu = formularz.cleaned_data.get('dokladnosc_reprezentacji_chromsomu')
                wielkosc_populacji = formularz.cleaned_data.get('wielkosc_populacji')
                liczba_epok = formularz.cleaned_data.get('liczba_epok')
                metoda_Selekcji = formularz.cleaned_data.get('metoda_Selekcji')
                implementacja_Krzyzowania = formularz.cleaned_data.get('implementacja_Krzyzowania')
                prawdopodbienstwo_Krzyzowania = formularz.cleaned_data.get('prawdopodbienstwo_Krzyzowania')
                implementacja_MutacjiBrzegowej = formularz.cleaned_data.get('implementacja_MutacjiBrzegowej')
                prawdopodbienstwo_MutacjiBrzegowej = formularz.cleaned_data.get('prawdopodbienstwo_MutacjiBrzegowej')
                ile_Przechodzi = formularz.cleaned_data.get('ile_Przechodzi')
                zakresMutacji2=formularz.cleaned_data.get('zakresMutacji2')
                zakresMutacji1 = formularz.cleaned_data.get('zakresMutacji1')
                if ile_Przechodzi is None:
                    ile_Przechodzi=30
                if zakresMutacji2 is None:
                    zakresMutacji2=3
                if zakresMutacji1 is None:
                    zakresMutacji1=-3

                rodzaj_Optymalizacj=formularz.cleaned_data.get('rodzaj_Optymalizacj')
                wielkosc_turnieju=formularz.cleaned_data.get('wielkosc_turnieju')
                elita=formularz.cleaned_data.get('elita')
                if wielkosc_turnieju is None:
                    wielkosc_turnieju=3

                if wielkosc_populacji-elita <= round(wielkosc_populacji*(ile_Przechodzi/100)):
                    elita=elita-round(wielkosc_populacji*(ile_Przechodzi/100))
               # ID_Wyniku= formularz.cleaned_data.get('ID_Wyniku')
                ustawienia=Ustawienia.objects.create(
                    zakres1 = zakres1,
                    zakres2 = zakres2,
                    wielkoscPopulacji = wielkosc_populacji,
                    liczbaepok = liczba_epok,
                    metodaSelekcji = metoda_Selekcji,
                    implementacjaKrzyzowania = implementacja_Krzyzowania,
                    prawdobodobienstwoKrzyzowania = prawdopodbienstwo_Krzyzowania,
                    implementacjaMutowania = implementacja_MutacjiBrzegowej,
                    prawdobodobienstwoMutowania = prawdopodbienstwo_MutacjiBrzegowej,
                    ileprzechodzi = ile_Przechodzi,
                    rodzaj_Optymalizacj=rodzaj_Optymalizacj,
                    wielkosc_turnieju=wielkosc_turnieju,
                    elita=elita,
                    zakresMutacji1=zakresMutacji1,
                    zakresMutacji2=zakresMutacji2
                    #

                )

                return redirect('Main:wynik',licz(ustawienia))
        else:
            messages.warning(self.request, "Błędnie uzupełniony formularz")
            return redirect("Main:main")



class WynikDzialania(ListView):
    model = Epoka

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        id_wyniku = self.request.path.rsplit("/")
        id_wyniku=id_wyniku[-1]
        Wyniki = Wynik.objects.filter(id=id_wyniku)
        ustawienia= Wyniki[0].epoka_set.all()[0]
        lista_srednich=[]
        lista_odchylen = []
        iteracja= []
        czas=0
        for x in Wyniki[0].epoka_set.all():
            lista_srednich.append(float(x.sredniWynik))
            lista_odchylen.append(str(x.odchylenieStandardowe))
            czas+=float(x.czas)
            tmp=x.iteracja.rsplit("/")
            tmp=tmp[0]
            iteracja.append(tmp)

        if(ustawienia.ustawienia.rodzaj_Optymalizacj=='Min'):
            maks=min(lista_srednich)
            najelpsza_epoka=lista_srednich.index(maks)+1
        else:
            maks = max(lista_srednich)
            najelpsza_epoka = lista_srednich.index(maks) + 1

        context= {"srednie": lista_srednich,
                   "odchylenie": lista_odchylen,
                   "Epoka": Wyniki[0].epoka_set.all(),
                   "iteracja":iteracja,
                   "czas":czas,
                   "ustawienia":ustawienia,
                    "maks":maks,
                    "najelpsza_epoka":najelpsza_epoka
                   }


        return context
    template_name = "Wynik.html"

class DetaleEpoki(DetailView):
        model = Epoka

        def get_context_data(self, **kwargs):
            context = super().get_context_data()
            lista_x = []
            lista_y = []
            lista_z = []


            for x in self.object.pojedynczawartoscwyniku_set.all():
                lista_x.append(x.x1)
                lista_y.append(x.x2)
                lista_z.append(x.wartosc)
            if self.object.ustawienia.rodzaj_Optymalizacj == "Min":
                najelpszyWyniki=self.object.pojedynczawartoscwyniku_set.all()[lista_z.index(min(lista_z))]
            else:
                najelpszyWyniki = self.object.pojedynczawartoscwyniku_set.all()[lista_z.index(max(lista_z))]
            context ['lista_x'] = lista_x
            context['lista_y'] =  lista_y
            context['lista_z'] =  lista_z
            context['zakres1'] = self.object.ustawienia.zakres1
            context['zakres2'] = self.object.ustawienia.zakres2
            context['min'] = min(lista_z)
            context['max'] = max(lista_z)
            context['najlepszy']=najelpszyWyniki

            return context

        template_name = "Epoka_detale.html"




class individual():
    cecha1 = 0
    cecha2 = 0
    wynik = 0


def funkcjaCelu(x1, x2):
    return pow((1.5-x1+x1*x2), 2) + pow((2.25-x1+x1*pow(x2,2)), 2) + pow((2.625-x1+x1*pow(x2, 3)),2)


def poczatkoweWartosci(populacja,zakres1,zakres2):
    lista= []
    for x in range(0,populacja):
        tmp = individual()
        tmp.cecha1=random.uniform(zakres1,zakres2)
        tmp.cecha2 = random.uniform(zakres1, zakres2)
        tmp.wynik=funkcjaCelu(tmp.cecha1, tmp.cecha2)
        lista.append(tmp)
    return lista


def selekcjaNajelpszychMAX(ustawienia,populacja=[]):
    licznik=round((ustawienia.ileprzechodzi/100)*populacja.__len__())
    najelpsze=[]
    Populacja_elity=[]
    populacja=sorted(populacja,key= lambda individual:individual.wynik,reverse=True)
    for i in range(0,ustawienia.elita):
        Populacja_elity.append(populacja[i])
    while najelpsze.__len__()!= ustawienia.wielkoscPopulacji-ustawienia.elita:
        najelpsze.append(populacja[random.randint(ustawienia.elita,ustawienia.elita + licznik)])

    return najelpsze,Populacja_elity

def selekcjaNajelpszychMIN(ustawienia, populacja=[]):
    licznik = round((ustawienia.ileprzechodzi / 100) * populacja.__len__())
    najelpsze = []
    Populacja_elity = []
    populacja = sorted(populacja, key=lambda individual: individual.wynik)
    for i in range(0, ustawienia.elita):
        Populacja_elity.append(populacja[i])
    while najelpsze.__len__() != ustawienia.wielkoscPopulacji - ustawienia.elita:
        najelpsze.append(populacja[random.randint(ustawienia.elita, ustawienia.elita + licznik)])

    return najelpsze, Populacja_elity


def selecjaTurniejowa(ustawienia, populacja=[]):
    answer = []
    lista_wynikow = []
    Populacja_elity = []
    if ustawienia.rodzaj_Optymalizacj=='Min':
        #elita

        for x in populacja:
            lista_wynikow.append(x.wynik)
        elita = heapq.nsmallest(ustawienia.elita, lista_wynikow)
        for i in elita:
            x = populacja[elita.index(i)]
            Populacja_elity.append(x)
            populacja.remove(x)
        lista_wynikow=[]
        # elita
        for x in populacja:
            lista_wynikow.append(x.wynik)
        while len(answer) < ustawienia.wielkoscPopulacji:
            tmp = random.sample(populacja, ustawienia.wielkosc_turnieju)
            best = max(lista_wynikow)
            for i in tmp:
                if i.wynik < best:
                    best = i.wynik
            answer.append(populacja[lista_wynikow.index(best)])
    else:
        # elita

        for x in populacja:
            lista_wynikow.append(x.wynik)
        elita = heapq.nlargest(ustawienia.elita, lista_wynikow)
        for i in elita:
            x = populacja[elita.index(i)]
            Populacja_elity.append(x)
            populacja.remove(x)
        lista_wynikow = []
        # elita
        for x in populacja:
            lista_wynikow.append(x.wynik)
        while len(answer) < ustawienia.wielkoscPopulacji:
            tmp=random.sample(populacja, ustawienia.wielkosc_turnieju)
            best=0
            for i in tmp:
                if i.wynik >best:
                    best=i.wynik
            answer.append(populacja[lista_wynikow.index(best)])
    return answer,Populacja_elity


def selekcjaKolemRuletki(ustawienia,populacja=[]):
    score={}
    lista_wynikow=[]
    Populacja_elity=[]
    najlepsi=[]
    if ustawienia.rodzaj_Optymalizacj=="Max":
        # elita

        for x in populacja:
            lista_wynikow.append(x.wynik)
        elita = heapq.nlargest(ustawienia.elita, lista_wynikow)
        for i in elita:
            x = populacja[elita.index(i)]
            Populacja_elity.append(x)
            populacja.remove(x)
            lista_wynikow = []
        # elita
        for indiv in populacja:
            score.update({indiv:indiv.wynik})
        for x in range(0,populacja.__len__()):
         najlepsi.append(rouletteWheelSelect(getRouletteWheel(populacja,score)))
    else:
        if ustawienia.rodzaj_Optymalizacj == "Min":
            # elita

            for x in populacja:
                lista_wynikow.append(x.wynik)
            elita = heapq.nsmallest(ustawienia.elita, lista_wynikow)
            for i in elita:
                x = populacja[elita.index(i)]
                Populacja_elity.append(x)
                populacja.remove(x)
                lista_wynikow=[]
            # elita
            for indiv in populacja:
                score.update({indiv: 1/indiv.wynik})
            for x in range(0, populacja.__len__()):
                najlepsi.append(rouletteWheelSelect(getRouletteWheel(populacja, score)))
    return najlepsi,Populacja_elity


def implementacjaKrzyzowania(typ,ustawienia, populacja=[]):
    nowePokolenie=[]
    # Krzyzowanie aarytmetnyczne
    if typ=="KA":
        punktKrzyzowania = random.uniform(0, 1)
        while nowePokolenie.__len__() < ustawienia.wielkoscPopulacji-ustawienia.elita:
            firstIndiv=random.randint(0,ustawienia.wielkoscPopulacji-ustawienia.elita-1)
            secondIndiv=random.randint(0,ustawienia.wielkoscPopulacji-ustawienia.elita-1)
            chromosom1cecha1bin = populacja[firstIndiv].cecha1
            chromosom1cecha2bin = populacja[firstIndiv].cecha2
            chromosom2cecha1bin = populacja[secondIndiv].cecha1
            chromosom2cecha2bin = populacja[secondIndiv].cecha2
            potomek1cecha1 = (punktKrzyzowania * chromosom1cecha1bin) + (1 - punktKrzyzowania) * chromosom2cecha1bin
            potomek1cecha2 = (punktKrzyzowania * chromosom1cecha2bin) + (1 - punktKrzyzowania) * chromosom2cecha2bin
            potomek2cecha1 = (1 - punktKrzyzowania) * chromosom1cecha1bin + punktKrzyzowania * chromosom2cecha1bin
            potomek2cecha2 = (1 - punktKrzyzowania) * chromosom1cecha2bin + punktKrzyzowania * chromosom2cecha2bin

            tmp = individual()
            tmp.cecha1 = potomek1cecha1
            tmp.cecha2 = potomek1cecha2
            tmp.wynik = funkcjaCelu(tmp.cecha1, tmp.cecha2)
            nowePokolenie.append(tmp)
            tmp = individual()
            tmp.cecha1 = potomek2cecha1
            tmp.cecha2 = potomek2cecha2
            tmp.wynik = funkcjaCelu(tmp.cecha1, tmp.cecha2)
            nowePokolenie.append(tmp)


    #krzyzowanie heurstyczne
    if typ=="KH":

        while nowePokolenie.__len__() != ustawienia.wielkoscPopulacji- ustawienia.elita:
            punktKrzyzowania = random.uniform(0, 1)
            i=random.randint(0,populacja.__len__()-1)
            j = random.randint(0, populacja.__len__() - 1)

            chromosom1cecha1bin = populacja[i].cecha1
            chromosom1cecha2bin = populacja[i].cecha2
            chromosom2cecha1bin = populacja[j].cecha1
            chromosom2cecha2bin = populacja[j].cecha2


            if chromosom2cecha1bin > chromosom1cecha1bin  and chromosom1cecha2bin < chromosom2cecha2bin:
                potomek1cecha1 = punktKrzyzowania * (chromosom2cecha1bin - chromosom1cecha1bin) + chromosom1cecha1bin
                potomek1cecha2 = punktKrzyzowania * (chromosom2cecha2bin - chromosom1cecha2bin) + chromosom1cecha2bin
                tmp = individual()
                tmp.cecha1 = potomek1cecha1
                tmp.cecha2 = potomek1cecha2
                tmp.wynik = funkcjaCelu(tmp.cecha1, tmp.cecha2)
                nowePokolenie.append(tmp)


    return nowePokolenie


def implementacjaMutacji(typ,ustawienia,populacja=[]):
    nowePokolenie=[]
    #Mutacja rownomierna
    if typ == "MR":
        for x in populacja:
            if random.uniform(0,100)<=ustawienia.prawdobodobienstwoMutowania:
                if random.random()==0:
                    new_x=random.uniform(ustawienia.zakresMutacji1,ustawienia.zakresMutacji2)
                    new_y=x.cecha2
                else:
                    new_x = x.cecha1
                    new_y = random.uniform(ustawienia.zakresMutacji1, ustawienia.zakresMutacji2)

                tmp=individual()
                tmp.cecha1 = new_x
                tmp.cecha2 = new_y
                tmp.wynik = funkcjaCelu(tmp.cecha1, tmp.cecha2)
                nowePokolenie.append(tmp)
            else:
                nowePokolenie.append(x)
    #Mutacja przez zamiania
    if typ == "MZ":
        for x in populacja:
            if random.uniform(0, 100) <= ustawienia.prawdobodobienstwoMutowania:
                new_x =x.cecha2
                new_y = x.cecha1
                tmp=individual()
                tmp.cecha1 = new_x
                tmp.cecha2 = new_y
                tmp.wynik = funkcjaCelu(tmp.cecha1, tmp.cecha2)
                nowePokolenie.append(tmp)

            else:
                nowePokolenie.append(x)
    return nowePokolenie


def licz(ustawienia):
    saving_time=0
    wynikFinalny=Wynik.objects.create()
    populacja=poczatkoweWartosci(ustawienia.wielkoscPopulacji,ustawienia.zakres1,ustawienia.zakres2)
    for i in range(ustawienia.liczbaepok):
        startime2 = timezone.now()
        czasselekcji=0
        czasmutowania=0
        czaskrzyzowania=0
        if ustawienia.metodaSelekcji== "SN":
            if(ustawienia.rodzaj_Optymalizacj=="Min"):
                startime= timezone.now()
                populacja,elita=selekcjaNajelpszychMIN(ustawienia,populacja)
                czasselekcji=timezone.now()-startime
                if random.uniform(0,100)<=ustawienia.prawdobodobienstwoKrzyzowania:
                    startime = timezone.now()
                    populacja = implementacjaKrzyzowania(ustawienia.implementacjaKrzyzowania,ustawienia,populacja)
                    czaskrzyzowania = timezone.now() - startime
                    startime = timezone.now()
                populacja = implementacjaMutacji(ustawienia.implementacjaMutowania,ustawienia,populacja)
                czasmutowania = timezone.now() - startime

                populacja=populacja+elita
            else:
                startime = timezone.now()
                populacja,elita = selekcjaNajelpszychMAX(ustawienia, populacja)
                czasselekcji = timezone.now() - startime
                if random.uniform(0, 100) <= ustawienia.prawdobodobienstwoKrzyzowania:
                    startime = timezone.now()
                    populacja = implementacjaKrzyzowania(ustawienia.implementacjaKrzyzowania,ustawienia,populacja)
                    czaskrzyzowania = timezone.now() - startime
                startime = timezone.now()
                populacja = implementacjaMutacji(ustawienia.implementacjaMutowania,ustawienia,populacja)
                czasmutowania = timezone.now() - startime

                populacja=populacja+elita
        else:
            if ustawienia.metodaSelekcji== "SR":
                startime = timezone.now()
                populacja,elita = selekcjaKolemRuletki(ustawienia,populacja)
                czasselekcji = timezone.now() - startime
                if random.uniform(0, 100) <= ustawienia.prawdobodobienstwoKrzyzowania:
                    startime = timezone.now()
                    populacja = implementacjaKrzyzowania(ustawienia.implementacjaKrzyzowania,ustawienia,populacja)
                    czaskrzyzowania = timezone.now() - startime
                startime = timezone.now()
                populacja = implementacjaMutacji(ustawienia.implementacjaMutowania, ustawienia, populacja)
                czasmutowania = timezone.now() - startime

                populacja=populacja+elita
            else:
                if ustawienia.metodaSelekcji == "ST":
                    startime = timezone.now()
                    populacja,elita = selecjaTurniejowa(ustawienia, populacja)
                    czasselekcji = timezone.now() - startime
                    if random.uniform(0, 100) <= ustawienia.prawdobodobienstwoKrzyzowania:
                        startime = timezone.now()
                        populacja = implementacjaKrzyzowania(ustawienia.implementacjaKrzyzowania,ustawienia,populacja)
                        czaskrzyzowania = timezone.now() - startime
                    startime = timezone.now()
                    populacja = implementacjaMutacji(ustawienia.implementacjaMutowania,ustawienia,populacja)
                    czasmutowania = timezone.now() - startime

                    populacja=populacja+elita






        sredniwynik = 0
        listawynikow=[]
        listax=[]
        listay=[]
        listaz=[]

        for x in populacja:
            sredniwynik += x.wynik
            listawynikow.append(x.wynik)
            listax.append(x.cecha1)
            listay.append(x.cecha2)
            listaz.append(x.wynik)



        ustawienia.save()
        czas=timezone.now()-startime2
        czasselekcji=str(czasselekcji).split(".")
        czasmutowania = str(czasmutowania).split(".")
        czaskrzyzowania = str(czaskrzyzowania).split(".")
        sekundys = str(czasselekcji[0].rsplit(":")[-1])
        sekundym = str(czasmutowania[0].rsplit(":")[-1])
        sekundyk = str(czaskrzyzowania[0].rsplit(":")[-1])
        setness = czasselekcji[-1]
        setnesm = czasmutowania[-1]
        setnesk = czaskrzyzowania[-1]
        print("Czas selekcji:" +sekundys +"."+setness)
        print("Czas Krzyzowania:"+ sekundyk+"."+setnesk)
        print("Czas mutowania:"+sekundym+"."+setnesm)
        czas= str(czas).split(".")
        sekundy=str(czas[0].rsplit(":")[-1])
        setnes=czas[-1]
        czas=sekundy+"."+setnes
        wyniki_epoki = Epoka.objects.create(

            czas=czas,
            iteracja=str(i + 1) + "/" + str(ustawienia.liczbaepok),
            sredniWynik=str(sredniwynik / populacja.__len__()),
            odchylenieStandardowe=statistics.stdev(listawynikow),
            rezultaty=wynikFinalny,
            ustawienia=ustawienia
        )
        ZapisWyników=[]
        startime=timezone.now()

        for x in populacja:
            ZapisWyników.append(PojedynczaWartoscWyniku(
             wartosc = x.wynik,
             x1 = x.cecha1,
             x2 = x.cecha2,
             Wynik=  wyniki_epoki
              ))
        PojedynczaWartoscWyniku.objects.bulk_create(ZapisWyników)
        czaszapisu=timezone.now()-startime
        czaszapisu=str(czaszapisu).split(".")
        sekundys = str(czaszapisu[0].rsplit(":")[-1])
        setness = czaszapisu[-1]
        print("Czas zapisu:" + sekundys + "." + setness)

        ustawienia.nalezy_do=wyniki_epoki
        wyniki_epoki.save()
        print(wyniki_epoki.iteracja)
    return wynikFinalny.id