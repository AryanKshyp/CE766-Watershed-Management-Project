# Rabi irrigation and dry-season river flow in the Subarnarekha watershed

## Problem statement

How much monsoon water can upland farmers store for a rabi crop while leaving enough in the river for Jamshedpur? I studied the 12,785 km² Subarnarekha watershed above the Jamshedpur gauge in Jharkhand, including its Kharkai tributary. I chose it partly because I come from nearby Bokaro. I recognised the same problem here as around Bokaro, where upstream farms and a steel city depend on the same river.

After the proposal feedback, I shifted from predicting flow at 31 gauges to comparing decisions in one watershed. I kept the watershed, the 1980–2018 record and the four interventions from my preliminary submission. For the final project I compared hypothetical investments above Chandil, where storing water for farmers could also affect releases to Jamshedpur. I asked which mix would irrigate the most land after a poor monsoon, what it would cost, and how often the city and the river would receive their target flows.

## Data

I used CAMELS-IND v2.2 daily catchment-average rainfall and GLEAM potential evapotranspiration, along with Central Water Commission discharge at Jamshedpur (06008) and Adityapur on the Kharkai (06001). I converted discharge to mm/day using their respective drainage areas of 12,785 and 6,350 km². I also used the Jamshedpur catchment's tree cover (30.7%) and GLEAM actual evapotranspiration to check the long-term water balance.

I kept missing streamflow days blank. From June 1981 to May 2018, 35 complete June–May periods had at least 80% observed flow. I compared observed and modelled yields on matching days. Chandil's design storage and water allocation came from project documents. For costs I used Jharkhand NABARD rates and reported Jharkhand watershed works. The proposed works, crop requirements and daily release rules are scenarios.

## Methodology

Levers (L). I tested all 16 combinations of four investments above Chandil, including a baseline with no new works. Each option added 1,000 dobhas (210 m³ each, 2.1 m effective depth), 1,000 ha of trench-cum-bunds, 100 check dams (500 m³ each), or 1,000 ha of trees.

Relationships (R). I used the daily GR4J model (Perrin et al., 2003), with 1980 for warm-up, 1981–2009 for calibration and 2010–2018 for validation at both gauges. Its baseline water balance is

P + F = AET + Q + ΔS

P is rainfall, F is net groundwater exchange (positive for a gain), AET is actual evapotranspiration, Q is runoff and ΔS is the daily change in stored water, including water in transit. All terms are in mm per day.

Ponds collect runoff from 1 ha each. Bunds return 30% of runoff from treated land to the routing store. Check dams receive streamflow from 10 ha each. Stored water can evaporate, seep back into routing, spill or supply irrigation. I spread withdrawals of up to one storage volume across October–February. For trees I scaled potential evapotranspiration using the change in the Zhang et al. (2001) annual evapotranspiration estimate.

I scaled Jamshedpur runoff to Chandil's 5,646 km² catchment. Separately modelled Kharkai and intervening runoff join downstream. Chandil's design live storage is 1,388 million cubic metres (MCM). Its daily balance is

ΔV = I − E − D − R − Spill

ΔV is the change in live storage, I inflow, E evaporation, D supply and R the controlled river release. I gave supply first priority, using Chandil's design allocation of 494 MCM/year as a constant demand proxy. The river release target was Chandil's drainage-area share of observed Q95.

Uncertainties (X). Twelve monsoons fell in the lowest third of June–September rainfall (≤970.4 mm). A combined stress case raised potential evapotranspiration by 10%, demand by 25%, seepage from 2 to 5 mm/day and crop water need from 375 to 450 mm. It halved available live capacity and the river release target. I varied capital costs by ±30%.

Measures (M). I divided irrigation volume by seasonal crop water need to obtain additional rabi hectares. I counted days meeting demand and January–May days meeting Q95 (3.05 m³/s, exceeded on 95% of observed days). I compared these measures and capital cost in ₹ crore across all years and deficient years.

## Results

Figure 1 shows how much water passed Jamshedpur in a year and how often the river delivered at least that much. At 75% dependability, the gauge gives 4,597 MCM and GR4J gives 5,597 MCM, about 22% higher. My preliminary values were 4,572 and 5,488 MCM. For the final calculation I excluded partial water years and the model warm-up, and included the complete year ending in May 2018. The interpretation holds. Across the 12 deficient years, GR4J averaged 4,660 MCM against 3,814 MCM observed. At Jamshedpur, Kling–Gupta efficiency fell from 0.88 in calibration to 0.79 in validation. A planner relying on GR4J alone would still count about a fifth too much water in dry years.

Figure 2 compares seven of the 16 portfolios after a deficient monsoon. In the reference case, ponds alone supplied the equivalent of 56.0 additional rabi hectares for ₹3.30 crore. Adding check dams brought this to 69.3 ha for ₹5.22 crore, also about 69.3 ha averaged across all 35 years. Adding bunds and trees brought the cost to ₹15.63 crore for the same irrigated area to one decimal place. Under combined stress, ponds supplied 44.9 ha and ponds with check dams supplied 56.0 ha in deficient years. All portfolios met the assumed city demand every day in both cases. In deficient years the river reached Q95 on only 36.4% of January–May days in the reference case and 16.9% under stress, including with no new works.

## Discussion

I'd start with ponds if the immediate aim is to irrigate a rabi crop. The extra ₹1.92 crore for check dams buys about 13 more hectares in the reference case. That gives farmers and the state a concrete choice. With the assumed ±30% range in unit costs, the combined investment could cost ₹3.65–6.78 crore. I would check local construction estimates and how many farmers can actually draw water before choosing sites.

The similar irrigation result across average and deficient years has a simple explanation. These are small structures and the model allows farmers to draw only one storage volume over the season. Ponds and check dams can reach that limit even in a relatively dry year. Bunds can improve soil moisture and trees can reduce erosion. I counted only irrigation supplied directly from storage, so the comparison gives no credit for those benefits or for well irrigation from recharge.

I would be more cautious about the city and the river. In the same 12 deficient years, Jamshedpur actually met Q95 on 92.2% of the 1,815 January–May days. The model with no new works gives 36.4%. Its release rule misses much of the dry-season flow that reached the gauge. It also gives the city first claim on storage and leaves out competing canal withdrawals, so 100% measures delivery of an assumed allocation. Identical percentages across these small investments tell me little about how far they could be expanded. I used the combined stress case to see how the result changes when several assumptions get worse together. These historical runs give no probability of a future shortage.

The water balance suggests where to look next. Over the retained years, rainfall minus observed runoff averaged 754 mm/year, close to the Zhang estimate of 741. GR4J's actual evapotranspiration was lower at 603 mm/year, against 672 from GLEAM, and the fitted model lost water through groundwater exchange. Daily Chandil inflows, storage, releases and actual abstractions would help separate regulation from model error. At farm level, measurements of pond storage after the monsoon, seepage and irrigated area would show whether the projected hectares are achievable.

## References and data/code repository

1. Mangukiya, N. K., et al. (2025). CAMELS-IND: hydrometeorological time series and catchment attributes for 228 catchments in Peninsular India. Earth System Science Data, 17, 461–491. [Paper](https://doi.org/10.5194/essd-17-461-2025) and [dataset v2.2](https://zenodo.org/records/14999580).
2. Perrin, C., Michel, C., and Andréassian, V. (2003). Improvement of a parsimonious model for streamflow simulation. Journal of Hydrology, 279, 275–289. [Paper](https://www.sciencedirect.com/science/article/pii/S0022169403002257).
3. Zhang, L., Dawes, W. R., and Walker, G. R. (2001). Response of mean annual evapotranspiration to vegetation changes at catchment scale. Water Resources Research, 37, 701–708. [Paper](https://doi.org/10.1029/2000WR900325).

The project repository contains the processed data, model code, cost and operating assumptions, and results for all 16 portfolios. [https://github.com/AryanKshyp/CE766-Watershed-Management-Project](https://github.com/AryanKshyp/CE766-Watershed-Management-Project).
