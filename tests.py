import pytest
from etl import parse_html

def test_parse_html():
    html = """
    <table class="table">
        <tr>
            <th>Team Name</th><th>Year</th><th>Wins</th><th>Losses</th><th>OT Losses</th><th>Win %</th><th>Goals For (GF)</th><th>Goals Against (GA)</th><th>+ / -</th>
        </tr>
        <tr>
            <td>Boston Bruins</td><td>1990</td><td>44</td><td>24</td><td>0</td><td>0.55</td><td>299</td><td>264</td><td>35</td>
        </tr>
    </table>
    """
    data = parse_html(html)
    assert len(data) == 1
    assert data[0] == {
        'Team Name': 'Boston Bruins',
        'Year': '1990',
        'Wins': '44',
        'Losses': '24',
        'OT Losses': '0',
        'Win %': '0.55',
        'Goals For (GF)': '299',
        'Goals Against (GA)': '264',
        '+ / -': '35'
    }

def test_winner_and_loser():
    data = [
        {'Team Name': 'Team A', 'Year': '1990', 'Wins': '10', 'Losses': '5', 'OT Losses': '0', 'Win %': '0.5', 'Goals For (GF)': '50', 'Goals Against (GA)': '40', '+ / -': '10'},
        {'Team Name': 'Team B', 'Year': '1990', 'Wins': '20', 'Losses': '10', 'OT Losses': '0', 'Win %': '0.66', 'Goals For (GF)': '70', 'Goals Against (GA)': '50', '+ / -': '20'},
        {'Team Name': 'Team C', 'Year': '1990', 'Wins': '5', 'Losses': '15', 'OT Losses': '0', 'Win %': '0.25', 'Goals For (GF)': '30', 'Goals Against (GA)': '60', '+ / -': '-30'}
    ]
    year = '1990'
    winner = max(data, key=lambda x: int(x['Wins']))
    loser = min(data, key=lambda x: int(x['Wins']))
    assert winner['Team Name'] == 'Team B'
    assert loser['Team Name'] == 'Team C'

if __name__ == "__main__":
    pytest.main()
