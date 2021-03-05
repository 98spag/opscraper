from flask import Flask, request, render_template, session, redirect, url_for
from collections import defaultdict
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

@app.route("/")
def index():
    return render_template("Index.html")

@app.route('/', methods=['POST'])
def scrape():
    ranks = []
    most_played = []
    most_played_champs = []
    lst = []

    results_rank = defaultdict(lambda: "")
    results_most_played = defaultdict(lambda: "")


    Player1 = request.form["Player1"]
    Player2 = request.form["Player2"]
    Player3 = request.form["Player3"]
    Player4 = request.form["Player4"]
    Player5 = request.form["Player5"]


    players = [Player1,Player2,Player3,Player4,Player5]
    players = list(filter(None, players))


    for i,player in enumerate(players):
        URL = "https://euw.op.gg/summoner/userName=" + player
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        check_existance = soup.find("h2", class_ = "Title")
        if check_existance is None:
            pass
        elif check_existance.text == "This summoner is not registered at OP.GG. Please check spelling.":
            return render_template("break.html", nonvalid = players[i],)


        # player info
        solo_rank = soup.find("div", class_="TierRank")
        if solo_rank is None:
            solo_rank = "Unranked"
            ranks.append(solo_rank)
        elif solo_rank.text == "\n\t\t\tUnranked\n\t\t":
            solo_rank = soup.find_all("li", class_="Item tip")
            for entry in solo_rank:
                if entry.find("b", string="S2020"):
                    solo_rank = entry
                    solo_rank_adj = solo_rank.text[-(len(solo_rank.text)-2):]
                    ranks.append(solo_rank_adj)
        else:
            ranks.append(solo_rank.text)



        URL = "https://euw.op.gg/summoner/champions/userName=" + player
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        champions_played_most = soup.find_all("tr", class_="Row TopRanker")
        for i, x in enumerate(champions_played_most):
            champion = x.find("td", class_="ChampionName Cell")
            pre = champion.text
            adj_champion = pre.replace("\n", "")
            most_played.append(adj_champion)
        most_played_champs.append(most_played)
        most_played = []



    for i, x in enumerate(ranks):
        results_rank[players[i]] = x
    for i, x in enumerate(most_played_champs):
        for entry in x:
            if entry == "Kai\u0027Sa":
                adj_entry = entry.replace("\u0027", "")
                lst.append(adj_entry)
            elif entry == "":
                lst.append("")
            else:
                lst.append(entry)
        results_most_played[players[i]] = lst[0] + ", " + lst[1] + ", " + lst[2]
        lst = []

    if Player1 != "":
        session["Player1"] = players[0]
    if Player2 != "":
        session["Player2"] = players[1]
    if Player3 != "":
        session["Player3"] = players[2]
    if Player4 != "":
        session["Player4"] = players[3]
    if Player5 != "":
        session["Player5"] = players[4]


    return render_template("page2.html", ranks = results_rank, Players = players, most_played = results_most_played)
    return redirect(url_for('details'))


@app.route('/details')
def details():
    ranks_flex = []
    win_ratio_soloq = []
    win_ratio_flexi = []

    results_rank_flex = defaultdict(lambda: "")
    results_win_ratio_soloq = defaultdict(lambda: "")
    results_win_ratio_flex = defaultdict(lambda: "")

    Player1 = session.get("Player1", None)
    Player2 = session.get("Player2", None)
    Player3 = session.get("Player3", None)
    Player4 = session.get("Player4", None)
    Player5 = session.get("Player5", None)


    players = [Player1, Player2, Player3, Player4, Player5]
    players = list(filter(None, players))

    for i, player in enumerate(players):
        URL = "https://euw.op.gg/summoner/userName=" + player
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        check_existance = soup.find("h2", class_="Title")
        if check_existance is None:
            pass
        elif check_existance.text == "This summoner is not registered at OP.GG. Please check spelling.":
            return render_template("break.html", nonvalid=players[i],)

            # flex rank
        rank_flex = soup.find("div", class_="sub-tier__info")
        if rank_flex is None:
            ranks_flex.append("no details found")
        else:
            rank_flexq = rank_flex.find("div", class_="sub-tier__rank-tier")
            pre_r = rank_flexq.text
            adj_r = pre_r.replace("\n", "")
            ranks_flex.append(adj_r.strip())

        # win ratios
        tier_info_solo = soup.find("div", class_="TierInfo")
        if tier_info_solo is None:
            win_ratio_soloq.append("no details found")
        else:
            win_ratio_solo = tier_info_solo.find("span", class_="winratio")
            win_ratio_soloq.append(win_ratio_solo.text)

        tier_info_flex = soup.find("div", class_="sub-tier__info")

        if tier_info_flex is None:
            win_ratio_flexi.append("no details found")
        else:
            win_ratio_flex = tier_info_flex.find("div", class_="sub-tier__gray-text")
            if win_ratio_flex is None:
                win_ratio_flexi.append("no details found")
            else:
                pre_wr = win_ratio_flex.text
                adj_wr = pre_wr.replace("\n", "")
                win_ratio_flexi.append(adj_wr.strip())

        for i, x in enumerate(ranks_flex):
            results_rank_flex[players[i]] = x
        for i, x in enumerate(win_ratio_soloq):
            results_win_ratio_soloq[players[i]] = x
        for i, x in enumerate(win_ratio_flexi):
            results_win_ratio_flex[players[i]] = x


    return render_template("details.html",Players = players, win_ratio_soloq = results_win_ratio_soloq, win_ratio_flexi = results_win_ratio_flex, ranks_flex = results_rank_flex)

@app.route('/loading')
def loading():
    return render_template("loading.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

