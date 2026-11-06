# Phase 0 audit
Generated: 2026-11-06 11:40:21 

## 1) Raw file arrangement
- DATASET/raw/cepii_gravity:
  - Countries_V202211.csv
  - Gravity_V202211.csv
  - Label_gdp_source_d_V202211.csv
  - Label_gdp_source_o_V202211.csv
  - Label_legal_new_d_V202211.csv
  - Label_legal_new_o_V202211.csv
  - Label_legal_old_d_V202211.csv
  - Label_legal_old_o_V202211.csv
  - Label_pop_source_d_V202211.csv
  - Label_pop_source_o_V202211.csv
  - Label_rta_coverage_V202211.csv
  - Label_rta_type_V202211.csv
- DATASET/raw/cow_mid:
- DATASET/raw/cow_states:
- DATASET/raw/international_results:
  - results.csv
- DATASET/raw/transfermarkt:
  - appearances.csv
  - club_games.csv
  - clubs.csv
  - competitions.csv
  - countries.csv
  - game_events.csv
  - game_lineups.csv
  - games.csv
  - national_teams.csv
  - player_valuations.csv
  - players.csv
  - results.csv
  - transfers.csv

Missing requested sources noted at this stage:
- `DATASET/raw/cow_mid/` is not present on disk; no COW MIDs files were found.
- `DATASET/raw/cow_states/` is not present on disk; no COW states files were found.

## 2) Year coverage by source
- appearances.csv: 2012-07-03 to 2026-06-28
- cepii_gravity/Gravity_V202211.csv: 1948 to 2021
- game_events.csv: 2006-06-09 to 2026-07-06
- game_lineups.csv: 2013-07-02 to 2026-07-06
- games.csv: 2006-06-09 to 2026-07-06
- international_results/results.csv: 1872-11-30 to 2026-10-06
- player_valuations.csv: 2000-01-20 to 2026-06-12
- results.csv: 1872-11-30 to 2026-10-06
- transfers.csv: 1993-07-01 to 2030-06-30

### Recommended overlap window
- Recommended analytic overlap for `transfermarkt` + `CEPII gravity` is 1993-2021 (matching the earliest transfer dates and the latest CEPII year coverage).
- If COW MIDs are supplied later, the overlap with conflict data should be restricted to 1993-2014, because COW MID ends in 2014.
- For match-level fixture analysis, the full fixture series runs from 1872 onward, but geopolitics and MIDs are only usable from the modern era.

## DATASET/raw/transfermarkt/appearances.csv
- Shape: (1894350, 13)
- Columns:
  - `appearance_id`: str
  - `game_id`: int64
  - `player_id`: int64
  - `player_club_id`: int64
  - `player_current_club_id`: int64
  - `date`: str
  - `player_name`: str
  - `competition_id`: str
  - `yellow_cards`: int64
  - `red_cards`: int64
  - `goals`: int64
  - `assists`: int64
  - `minutes_played`: int64
- Missing values (top 10): `player_name`=2, `appearance_id`=0, `game_id`=0, `player_id`=0, `player_club_id`=0, `player_current_club_id`=0, `date`=0, `competition_id`=0, `yellow_cards`=0, `red_cards`=0
- Date/year range: 2012-07-03 to 2026-06-28
- Key uniqueness: `player_id`=29531; `competition_id`=48; `game_id`=73426; `date`=4108

## DATASET/raw/transfermarkt/club_games.csv
- Shape: (177916, 11)
- Columns:
  - `game_id`: int64
  - `club_id`: int64
  - `own_goals`: int64
  - `own_position`: float64
  - `own_manager_name`: str
  - `opponent_id`: int64
  - `opponent_goals`: int64
  - `opponent_position`: float64
  - `opponent_manager_name`: str
  - `hosting`: str
  - `is_win`: int64
- Missing values (top 10): `own_position`=50754, `opponent_position`=50754, `own_manager_name`=1688, `opponent_manager_name`=1688, `game_id`=0, `club_id`=0, `own_goals`=0, `opponent_id`=0, `opponent_goals`=0, `hosting`=0
- Date/year range: N/A
- Key uniqueness: `club_id`=3274; `game_id`=88958

## DATASET/raw/transfermarkt/clubs.csv
- Shape: (796, 17)
- Columns:
  - `club_id`: int64
  - `club_code`: str
  - `name`: str
  - `domestic_competition_id`: str
  - `total_market_value`: float64
  - `squad_size`: int64
  - `average_age`: float64
  - `foreigners_number`: int64
  - `foreigners_percentage`: float64
  - `national_team_players`: int64
  - `stadium_name`: str
  - `stadium_seats`: int64
  - `net_transfer_record`: str
  - `coach_name`: str
  - `last_season`: int64
  - `filename`: str
  - `url`: str
- Missing values (top 10): `total_market_value`=796, `coach_name`=393, `foreigners_percentage`=60, `average_age`=38, `stadium_name`=0, `filename`=0, `last_season`=0, `net_transfer_record`=0, `stadium_seats`=0, `club_id`=0
- Date/year range: N/A
- Key uniqueness: `club_id`=796

## DATASET/raw/transfermarkt/competitions.csv
- Shape: (65, 11)
- Columns:
  - `competition_id`: str
  - `competition_code`: str
  - `name`: str
  - `sub_type`: str
  - `type`: str
  - `country_id`: int64
  - `country_name`: str
  - `domestic_league_code`: str
  - `confederation`: str
  - `total_clubs`: float64
  - `url`: str
- Missing values (top 10): `total_clubs`=15, `country_name`=12, `domestic_league_code`=12, `competition_id`=0, `competition_code`=0, `name`=0, `sub_type`=0, `type`=0, `country_id`=0, `confederation`=0
- Date/year range: N/A
- Key uniqueness: `competition_id`=65; `country_id`=32; `country_name`=32

## DATASET/raw/transfermarkt/countries.csv
- Shape: (124, 8)
- Columns:
  - `country_id`: int64
  - `country_name`: str
  - `country_code`: str
  - `confederation`: str
  - `total_clubs`: int64
  - `total_players`: int64
  - `average_age`: float64
  - `url`: str
- Missing values (top 10): `country_id`=0, `country_name`=0, `country_code`=0, `confederation`=0, `total_clubs`=0, `total_players`=0, `average_age`=0, `url`=0
- Date/year range: N/A
- Key uniqueness: `country_id`=124; `country_name`=124

## DATASET/raw/transfermarkt/game_events.csv
- Shape: (1274469, 11)
- Columns:
  - `game_event_id`: str
  - `date`: str
  - `game_id`: int64
  - `minute`: int64
  - `type`: str
  - `club_id`: int64
  - `club_name`: str
  - `player_id`: int64
  - `description`: str
  - `player_in_id`: float64
  - `player_assist_id`: float64
- Missing values (top 10): `player_assist_id`=1086191, `player_in_id`=643922, `description`=93157, `game_event_id`=0, `date`=0, `game_id`=0, `minute`=0, `type`=0, `club_id`=0, `club_name`=0
- Date/year range: 2006-06-09 to 2026-07-06
- Key uniqueness: `player_id`=74555; `club_id`=3170; `game_id`=88813; `date`=4443

## DATASET/raw/transfermarkt/game_lineups.csv
- Shape: (3179016, 10)
- Columns:
  - `game_lineups_id`: str
  - `date`: str
  - `game_id`: int64
  - `player_id`: int64
  - `club_id`: int64
  - `player_name`: str
  - `type`: str
  - `position`: str
  - `number`: object
  - `team_captain`: int64
- Missing values (top 10): `position`=3, `game_lineups_id`=0, `date`=0, `game_id`=0, `player_id`=0, `club_id`=0, `player_name`=0, `type`=0, `number`=0, `team_captain`=0
- Date/year range: 2013-07-02 to 2026-07-06
- Key uniqueness: `player_id`=114893; `club_id`=3144; `game_id`=81197; `date`=3967

## DATASET/raw/transfermarkt/games.csv
- Shape: (88958, 23)
- Columns:
  - `game_id`: int64
  - `competition_id`: str
  - `season`: int64
  - `round`: str
  - `date`: str
  - `home_club_id`: int64
  - `away_club_id`: int64
  - `home_club_goals`: int64
  - `away_club_goals`: int64
  - `home_club_position`: float64
  - `away_club_position`: float64
  - `home_club_manager_name`: str
  - `away_club_manager_name`: str
  - `stadium`: str
  - `attendance`: float64
  - `referee`: str
  - `url`: str
  - `home_club_formation`: str
  - `away_club_formation`: str
  - `home_club_name`: str
  - `away_club_name`: str
  - `aggregate`: str
  - `competition_type`: str
- Missing values (top 10): `home_club_position`=25377, `away_club_position`=25377, `attendance`=10803, `home_club_formation`=8200, `away_club_formation`=8073, `competition_type`=1214, `away_club_manager_name`=844, `home_club_manager_name`=844, `referee`=678, `stadium`=242
- Date/year range: 2006-06-09 to 2026-07-06
- Key uniqueness: `competition_id`=70; `game_id`=88958; `date`=4445

## DATASET/raw/transfermarkt/national_teams.csv
- Shape: (124, 17)
- Columns:
  - `national_team_id`: int64
  - `name`: str
  - `team_code`: str
  - `country_id`: int64
  - `country_name`: str
  - `country_code`: str
  - `confederation`: str
  - `team_image_url`: str
  - `squad_size`: int64
  - `average_age`: float64
  - `foreigners_number`: int64
  - `foreigners_percentage`: float64
  - `total_market_value`: float64
  - `coach_name`: float64
  - `fifa_ranking`: int64
  - `last_season`: int64
  - `url`: str
- Missing values (top 10): `coach_name`=124, `foreigners_percentage`=8, `total_market_value`=4, `confederation`=1, `national_team_id`=0, `average_age`=0, `last_season`=0, `fifa_ranking`=0, `foreigners_number`=0, `squad_size`=0
- Date/year range: N/A
- Key uniqueness: `country_id`=124; `country_name`=124

## DATASET/raw/transfermarkt/player_valuations.csv
- Shape: (656301, 6)
- Columns:
  - `player_id`: int64
  - `date`: str
  - `market_value_in_eur`: int64
  - `current_club_name`: str
  - `current_club_id`: int64
  - `player_club_domestic_competition_id`: str
- Missing values (top 10): `player_club_domestic_competition_id`=92973, `player_id`=0, `date`=0, `market_value_in_eur`=0, `current_club_name`=0, `current_club_id`=0
- Date/year range: 2000-01-20 to 2026-06-12
- Key uniqueness: `player_id`=41528; `date`=5749

## DATASET/raw/transfermarkt/players.csv
- Shape: (50149, 26)
- Columns:
  - `player_id`: int64
  - `first_name`: str
  - `last_name`: str
  - `name`: str
  - `last_season`: int64
  - `current_club_id`: int64
  - `player_code`: str
  - `country_of_birth`: str
  - `city_of_birth`: str
  - `country_of_citizenship`: str
  - `date_of_birth`: str
  - `sub_position`: str
  - `position`: str
  - `foot`: str
  - `height_in_cm`: float64
  - `contract_expiration_date`: str
  - `agent_name`: str
  - `image_url`: str
  - `international_caps`: float64
  - `international_goals`: float64
  - `current_national_team_id`: float64
  - `url`: str
  - `current_club_domestic_competition_id`: str
  - `current_club_name`: str
  - `market_value_in_eur`: float64
  - `highest_market_value_in_eur`: float64
- Missing values (top 10): `current_national_team_id`=46889, `international_goals`=30793, `international_caps`=30793, `agent_name`=23296, `contract_expiration_date`=18569, `highest_market_value_in_eur`=8621, `market_value_in_eur`=8621, `foot`=5893, `country_of_birth`=5885, `city_of_birth`=5608
- Date/year range: N/A
- Key uniqueness: `player_id`=50149

## DATASET/raw/transfermarkt/results.csv
- Shape: (49940, 9)
- Columns:
  - `date`: str
  - `home_team`: str
  - `away_team`: str
  - `home_score`: int64
  - `away_score`: int64
  - `tournament`: str
  - `city`: str
  - `country`: str
  - `neutral`: bool
- Missing values (top 10): `date`=0, `home_team`=0, `away_team`=0, `home_score`=0, `away_score`=0, `tournament`=0, `city`=0, `country`=0, `neutral`=0
- Date/year range: 1872-11-30 to 2026-10-06
- Key uniqueness: `home_team`=328; `away_team`=322; `date`=16538

## DATASET/raw/transfermarkt/transfers.csv
- Shape: (175165, 10)
- Columns:
  - `player_id`: int64
  - `transfer_date`: str
  - `transfer_season`: str
  - `from_club_id`: int64
  - `to_club_id`: int64
  - `from_club_name`: str
  - `to_club_name`: str
  - `transfer_fee`: float64
  - `market_value_in_eur`: float64
  - `player_name`: str
- Missing values (top 10): `market_value_in_eur`=68160, `transfer_fee`=61526, `player_id`=0, `transfer_date`=0, `transfer_season`=0, `from_club_id`=0, `to_club_id`=0, `from_club_name`=0, `to_club_name`=0, `player_name`=0
- Date/year range: 1993-07-01 to 2030-06-30
- Key uniqueness: `player_id`=23379

## DATASET/raw/international_results/results.csv
- Shape: (49940, 9)
- Columns:
  - `date`: str
  - `home_team`: str
  - `away_team`: str
  - `home_score`: int64
  - `away_score`: int64
  - `tournament`: str
  - `city`: str
  - `country`: str
  - `neutral`: bool
- Missing values (top 10): `date`=0, `home_team`=0, `away_team`=0, `home_score`=0, `away_score`=0, `tournament`=0, `city`=0, `country`=0, `neutral`=0
- Date/year range: 1872-11-30 to 2026-10-06
- Key uniqueness: `home_team`=328; `away_team`=322; `date`=16538

## DATASET/raw/cepii_gravity/Countries_V202211.csv
- Shape: (252, 12)
- Columns:
  - `country_id`: str
  - `iso3`: str
  - `iso3num`: float64
  - `country`: str
  - `countrylong`: str
  - `first_year`: float64
  - `last_year`: float64
  - `countrygroup_iso3`: str
  - `countrygroup_iso3num`: float64
  - `iso2`: str
  - `heg_iso3_2020`: str
  - `heg_iso3num_2020`: float64
- Missing values (top 10): `last_year`=235, `heg_iso3_2020`=212, `heg_iso3num_2020`=212, `first_year`=209, `countrygroup_iso3`=197, `countrygroup_iso3num`=197, `iso3num`=1, `country_id`=0, `iso3`=0, `country`=0
- Date/year range: N/A
- Key uniqueness: `country_id`=252; `iso3`=243

## DATASET/raw/cepii_gravity/Gravity_V202211.csv
- Shape: (4699296, 87)
- Columns:
  - `year`: int64
  - `country_id_o`: str
  - `country_id_d`: str
  - `iso3_o`: str
  - `iso3_d`: str
  - `iso3num_o`: float64
  - `iso3num_d`: float64
  - `country_exists_o`: int64
  - `country_exists_d`: int64
  - `gmt_offset_2020_o`: float64
  - `gmt_offset_2020_d`: float64
  - `distw_harmonic`: float64
  - `distw_arithmetic`: float64
  - `distw_harmonic_jh`: float64
  - `distw_arithmetic_jh`: float64
  - `dist`: float64
  - `main_city_source_o`: str
  - `main_city_source_d`: str
  - `distcap`: float64
  - `contig`: float64
  - `diplo_disagreement`: float64
  - `scaled_sci_2021`: float64
  - `comlang_off`: float64
  - `comlang_ethno`: float64
  - `comcol`: float64
  - `col45`: float64
  - `legal_old_o`: float64
  - `legal_old_d`: float64
  - `legal_new_o`: float64
  - `legal_new_d`: float64
  - `comleg_pretrans`: float64
  - `comleg_posttrans`: float64
  - `transition_legalchange`: float64
  - `comrelig`: float64
  - `heg_o`: float64
  - `heg_d`: float64
  - `col_dep_ever`: float64
  - `col_dep`: float64
  - `col_dep_end_year`: float64
  - `col_dep_end_conflict`: float64
  - `empire`: str
  - `sibling_ever`: float64
  - `sibling`: float64
  - `sever_year`: float64
  - `sib_conflict`: float64
  - `pop_o`: float64
  - `pop_d`: float64
  - `gdp_o`: float64
  - `gdp_d`: float64
  - `gdpcap_o`: float64
  - `gdpcap_d`: float64
  - `pop_source_o`: float64
  - `pop_source_d`: float64
  - `gdp_source_o`: float64
  - `gdp_source_d`: float64
  - `gdp_ppp_o`: float64
  - `gdp_ppp_d`: float64
  - `gdpcap_ppp_o`: float64
  - `gdpcap_ppp_d`: float64
  - `pop_pwt_o`: float64
  - `pop_pwt_d`: float64
  - `gdp_ppp_pwt_o`: float64
  - `gdp_ppp_pwt_d`: float64
  - `gatt_o`: float64
  - `gatt_d`: float64
  - `wto_o`: float64
  - `wto_d`: float64
  - `eu_o`: float64
  - `eu_d`: float64
  - `fta_wto`: float64
  - `fta_wto_raw`: float64
  - `rta_coverage`: float64
  - `rta_type`: float64
  - `entry_cost_o`: float64
  - `entry_cost_d`: float64
  - `entry_proc_o`: float64
  - `entry_proc_d`: float64
  - `entry_time_o`: float64
  - `entry_time_d`: float64
  - `entry_tp_o`: float64
  - `entry_tp_d`: float64
  - `tradeflow_comtrade_o`: float64
  - `tradeflow_comtrade_d`: float64
  - `tradeflow_baci`: float64
  - `manuf_tradeflow_baci`: float64
  - `tradeflow_imf_o`: float64
  - `tradeflow_imf_d`: float64
- Missing values (top 10): `col_dep_end_conflict`=4682542, `col_dep_end_year`=4672808, `empire`=4605618, `rta_coverage`=4516499, `rta_type`=4516499, `sever_year`=4093988, `sib_conflict`=4077928, `tradeflow_baci`=4004468, `manuf_tradeflow_baci`=4004468, `distw_harmonic_jh`=3964086
- Date/year range: 1948 to 2021
- Key uniqueness: `year`=74

## DATASET/raw/cepii_gravity/Label_gdp_source_d_V202211.csv
- Shape: (3, 2)
- Columns:
  - `gdp_source_d`: int64
  - `gdp_source_d_lbl`: str
- Missing values (top 10): `gdp_source_d`=0, `gdp_source_d_lbl`=0
- Date/year range: N/A
- Key uniqueness: `gdp_source_d`=3; `gdp_source_d_lbl`=3

## DATASET/raw/cepii_gravity/Label_gdp_source_o_V202211.csv
- Shape: (3, 2)
- Columns:
  - `gdp_source_o`: int64
  - `gdp_source_o_lbl`: str
- Missing values (top 10): `gdp_source_o`=0, `gdp_source_o_lbl`=0
- Date/year range: N/A
- Key uniqueness: `gdp_source_o`=3; `gdp_source_o_lbl`=3

## DATASET/raw/cepii_gravity/Label_legal_new_d_V202211.csv
- Shape: (5, 2)
- Columns:
  - `legal_new_d`: int64
  - `legal_new_d_lbl`: str
- Missing values (top 10): `legal_new_d`=0, `legal_new_d_lbl`=0
- Date/year range: N/A
- Key uniqueness: `legal_new_d`=5; `legal_new_d_lbl`=5

## DATASET/raw/cepii_gravity/Label_legal_new_o_V202211.csv
- Shape: (5, 2)
- Columns:
  - `legal_new_o`: int64
  - `legal_new_o_lbl`: str
- Missing values (top 10): `legal_new_o`=0, `legal_new_o_lbl`=0
- Date/year range: N/A
- Key uniqueness: `legal_new_o`=5; `legal_new_o_lbl`=5

## DATASET/raw/cepii_gravity/Label_legal_old_d_V202211.csv
- Shape: (5, 2)
- Columns:
  - `legal_old_d`: int64
  - `legal_old_d_lbl`: str
- Missing values (top 10): `legal_old_d`=0, `legal_old_d_lbl`=0
- Date/year range: N/A
- Key uniqueness: `legal_old_d`=5; `legal_old_d_lbl`=5

## DATASET/raw/cepii_gravity/Label_legal_old_o_V202211.csv
- Shape: (5, 2)
- Columns:
  - `legal_old_o`: int64
  - `legal_old_o_lbl`: str
- Missing values (top 10): `legal_old_o`=0, `legal_old_o_lbl`=0
- Date/year range: N/A
- Key uniqueness: `legal_old_o`=5; `legal_old_o_lbl`=5

## DATASET/raw/cepii_gravity/Label_pop_source_d_V202211.csv
- Shape: (3, 2)
- Columns:
  - `pop_source_d`: int64
  - `pop_source_d_lbl`: str
- Missing values (top 10): `pop_source_d`=0, `pop_source_d_lbl`=0
- Date/year range: N/A
- Key uniqueness: `pop_source_d`=3; `pop_source_d_lbl`=3

## DATASET/raw/cepii_gravity/Label_pop_source_o_V202211.csv
- Shape: (3, 2)
- Columns:
  - `pop_source_o`: int64
  - `pop_source_o_lbl`: str
- Missing values (top 10): `pop_source_o`=0, `pop_source_o_lbl`=0
- Date/year range: N/A
- Key uniqueness: `pop_source_o`=3; `pop_source_o_lbl`=3

## DATASET/raw/cepii_gravity/Label_rta_coverage_V202211.csv
- Shape: (3, 2)
- Columns:
  - `rta_coverage`: int64
  - `rta_coverage_lbl`: str
- Missing values (top 10): `rta_coverage`=0, `rta_coverage_lbl`=0
- Date/year range: N/A
- Key uniqueness: `rta_coverage`=3; `rta_coverage_lbl`=3

## DATASET/raw/cepii_gravity/Label_rta_type_V202211.csv
- Shape: (6, 2)
- Columns:
  - `rta_type`: int64
  - `rta_type_lbl`: str
- Missing values (top 10): `rta_type`=0, `rta_type_lbl`=0
- Date/year range: N/A
- Key uniqueness: `rta_type`=6; `rta_type_lbl`=6

## 3) Transfermarkt destination universe for T1 (countries with a league)
- Count: 31
- Countries: Argentina, Australia, Austria, Belgium, Brazil, Croatia, Czech Republic, Denmark, England, France, Germany, Greece, Italy, Japan, Korea, South, Mexico, Netherlands, Norway, Poland, Portugal, Romania, Russia, Saudi Arabia, Scotland, Serbia, Spain, Sweden, Switzerland, Türkiye, Ukraine, United States

## 4) Immediate data gaps and risk flags
- `DATASET/raw/cow_mid/` and `DATASET/raw/cow_states/` are absent; these are required for the COW MID and COW-state harmonisation steps. I need those files before Phase 1 can be finished.
- The Transfermarkt competitions table exposes `country_name` for domestic leagues, but it does not contain a direct ISO3 mapping; country harmonisation will be needed. This is expected and manageable.
- The fixture results file appears to be a single international-results table and is duplicated in the Transfermarkt source folder; keep both but do not assume they are identical unless checked during Phase 2.

