import gjp

import math
import statistics
import numpy as np

def brier_score(probabilities, outcomes):
	return np.mean((probabilities-outcomes)**2)

class Aggregator:
	def __init__(self):
		self.aggr_methods=[]
		self.aggr_index=0
		self.extr=3
		means=['arith', 'geom', 'median']
		formats=['probs', 'odds', 'logodds']
		decay=['nodec', 'dec']
		extremize=['gjpextr', 'postextr', 'neyextr', 'befextr', 'noextr']
		for i1 in means:
			for i2 in formats:
				for i3 in decay:
					for i4 in extremize:
						#the first sometimes doesn't work (negative values)
						#the second is equivalent to the geometric mean of odds
						#I also don't know how to compute the weighted geometric mean/median
						if (i1=='geom' and i2=='logodds') or (i1=='arith' and i2=='logodds') or (i3=='dec' and i1!='arith'):
							continue
						self.aggr_methods.append([i1, i2, i3, i4])

	def aggregate(self, g):
		n=len(g)

		if n==0:
			return

		probabilities=g['probability']

		if 'befextr' in self.aggr_methods[self.aggr_index]:
			p=probabilities
			probabilities=((p**self.extr)/(((p**self.extr)+(1-p))**(1/self.extr)))

		if 'dec' in self.aggr_methods[self.aggr_index]:
			if 'NULL' in g['date_suspend']: #ARGH
				weights=np.ones_like(probabilities)
			else:
				t_diffs=g['date_suspend']-g['timestamp']
				t_diffs=np.array([t.total_seconds() for t in t_diffs])
				weights=0.99**(1/(1*86400)*t_diffs)
		else:
			weights=np.ones_like(probabilities)

		if 'odds' in self.aggr_methods[self.aggr_index]:
			probabilities=probabilities/(1-probabilities)
		elif 'logodds' in self.aggr_methods[self.aggr_index]:
			probabilities=probabilities/(1-probabilities)
			probabilities=np.log(probabilities)

		if 'arith' in self.aggr_methods[self.aggr_index]:
			aggrval=np.sum(weights*probabilities)/np.sum(weights)
		elif 'geom' in self.aggr_methods[self.aggr_index]:
			aggrval=statistics.geometric_mean(probabilities)
		elif 'median' in self.aggr_methods[self.aggr_index]:
			aggrval=np.median(probabilities)

		if 'odds' in self.aggr_methods[self.aggr_index]:
			aggrval=aggrval/(1+aggrval)
		elif 'logodds' in self.aggr_methods[self.aggr_index]:
			aggrval=np.exp(aggrval)
			aggrval=aggrval/(1+aggrval)

		if 'gjpextr' in self.aggr_methods[self.aggr_index]:
			p=aggrval
			aggrval=((p**self.extr)/(((p**self.extr)+(1-p))**(1/self.extr)))
		elif 'postextr' in self.aggr_methods[self.aggr_index]:
			p=aggrval
			aggrval=p**self.extr
		elif 'neyextr' in self.aggr_methods[self.aggr_index]:
			p=aggrval
			d=n*(math.sqrt(3*n**2-3*n+1)-2)/(n**2-n-1)
			aggrval=p**d

		return np.array([aggrval])

	def all_aggregations(self, forecasts):
		self.aggr_index=0
		results=dict()

		for i in range(0, len(self.aggr_methods)):
			res=gjp.calculate_aggregate_score(forecasts, self.aggregate, brier_score, norm=True)
			res=np.mean(res)
			results['_'.join(self.aggr_methods[self.aggr_index])]=res
			print(self.aggr_methods[self.aggr_index], res)
			self.aggr_index+=1

		results=[(results[k], k) for k in results.keys()]
		results.sort()

		return results

#survey_forecasts=gjp.get_comparable_survey_forecasts(gjp.survey_files)
#team_forecasts=survey_forecasts.loc[survey_forecasts['team_id'].notna()]
#nonteam_forecasts=survey_forecasts.loc[survey_forecasts['team_id'].isna()]
f=gjp.market_files[0]
market_forecasts=gjp.get_comparable_market_forecasts([f])

# broken: 0,1,2,3,4,5,6,7,8,9

a=Aggregator()

#print('all surveys:')
#a.all_aggregations(survey_forecasts)
#
#print('surveys teams:')
#a.all_aggregations(team_forecasts)
#
#print('surveys non-teams:')
#a.all_aggregations(nonteam_forecasts)
#
#print('all markets non-teams:')
#a.all_aggregations(market_forecasts)
