"""
Anomaly Lookup:
This module provides process flow functions for anomaly lookup.  Method - run is the main entry point.
It has dependency on .NET library: Microsoft.Azure.CIS.Notebooks.AnomalyLookup.
"""

import clr
clr.AddReference("System")
clr.AddReference('Newtonsoft.Json')
clr.AddReference("Microsoft.Azure.CIS.Notebooks.AnomalyLookup")

import copy
import datetime as dt
import pandas as pd
from pandas.io.json import json_normalize
import sys
import json
import ipywidgets as widgets
from ipywidgets import Button, GridBox, Layout, ButtonStyle
from azure.loganalytics.models import QueryBody
from azure.loganalytics import LogAnalyticsDataClient

from System import *
from Microsoft.Azure.CIS.Notebooks.AnomalyLookup import *
from Microsoft.Azure.CIS.Notebooks.LogHelper import *

from .anomaly_lookup_view_helper import *

class AnomalyLookup(object):
    def __init__(self, workspace_id, la_data_client):
        self.workspace_id = workspace_id
        self.la_data_client = la_data_client
        self.logger = AILogger()

    def query_table_list(self):
        return self.query_loganalytics(KqlLibrary.ListTables())

    def query_loganalytics(self, query):
        res = self.la_data_client.query(self.workspace_id, QueryBody(query=query))
        json = res.as_dict()
        cols = json_normalize(json['tables'][0], 'columns')
        df = json_normalize(json['tables'][0], 'rows')
        if (df.shape[0] != 0):
            df.columns = cols.name
        return df

    def construct_related_queries(self, dfAnomalies):
        if (dfAnomalies.shape[0] == 0):
            return

        queries = ''
        for tbl in dfAnomalies.Table.unique():

            curTableAnomalies = dfAnomalies.ix[dfAnomalies.Table == tbl,:]
            query = """{tbl} | where TimeGenerated > ago(60d) | where ingestion_time() > datetime({maxTimestamp})-1d and ingestion_time() < datetime({maxTimestamp}) | where {entCol} has "{qEntity}" | where """.format(**{
                'tbl': tbl,
                'qTimestamp': curTableAnomalies.qTimestamp.iloc[0],
                'maxTimestamp': curTableAnomalies.maxTimestamp.iloc[0],
                'entCol': curTableAnomalies.entCol.iloc[0],
                'qEntity': curTableAnomalies.qEntity.iloc[0]
            })

            for j, row in curTableAnomalies.iterrows():
                query += " {col} == to{colType}(\"{colVal}\") or".format(**{
                    'col': row.colName,
                    'colType': (row.colType) if 'colType' in row.keys() else 'string',
                    'colVal': row.colVal
                })

            query = query[:-2] # drop the last or
            query += " | take 1000" # limit the output size

            query = query.replace("\\","\\\\")
            #print(query + "\n\n")

            queries += query
        return queries

    def get_timewindow(self, qEntity, qTimestamp, entCol, tbl):
        # find the relevant time window for analysis
        winStart = 0
        minTimestamp = None
        delta = None
        maxTimestamp = None
        longMinTimestamp = None
        for f in range(-30, 0, 1):
            dfTimeRange = self.query_loganalytics(KqlLibrary.TimeWindowQuery(tbl, qTimestamp, entCol, qEntity, f, f+1, 'd'))
        
            if (dfTimeRange.shape[0] > 0):
                winStart = f
                break

        dtQTimestamp = pd.to_datetime(qTimestamp)
        ind2now = dt.datetime.utcnow() - dtQTimestamp
        if (winStart < -3):
            if (ind2now > dt.timedelta(days=1)):
                delta = '1d'
                maxTimestamp = dtQTimestamp + dt.timedelta(days=1)
            else:
                delta = '1d'
                maxTimestamp = dt.datetime.now()
            longMinTimestamp = maxTimestamp + dt.timedelta(days=winStart)
            minTimestamp = maxTimestamp + dt.timedelta(days=max([-6,winStart]))

        elif (winStart < 0): # switch to hours
            winStartH = -5
            for f in range(-3*24, -5, 1):
                dfTimeRange = self.query_loganalytics(KqlLibrary.TimeWindowQuery(tbl, qTimestamp, entCol, qEntity, f, f+1, 'h'))

                if (dfTimeRange.shape[0] > 0):
                    winStartH = f
                    break
            if (winStartH < -5):
                if (ind2now > dt.timedelta(hours=1)):
                    delta = '1h'
                    maxTimestamp = dtQTimestamp + dt.timedelta(hours=1)
                else:
                    delta = '1h'
                    maxTimestamp = dt.datetime.now()
                minTimestamp = maxTimestamp + dt.timedelta(hours=winStartH)
                longMinTimestamp = minTimestamp

        return minTimestamp, delta, maxTimestamp, longMinTimestamp

    def run(self, qTimestamp, qEntity, tables):
        progress_bar = AnomalyLookupViewHelper.define_int_progress_bar()
        display(progress_bar)

        # list tables if not given
        if (len(tables) == 0):
            tables = self.query_loganalytics(KqlLibrary.ListTables())
            tables = tables.TableName.tolist()

        progress_bar.value += 1

        # find the column in which the query entity appears in each table - assumption that it appears in just one columns
        tables2search = []
        for tbl in tables:
            print(tbl)
            entInTable = self.query_loganalytics(KqlLibrary.IsEntityInTable(tbl, qTimestamp, qEntity))
            if (entInTable.shape[0] > 0):
                entCol = [col for col in entInTable.select_dtypes('object').columns[1:] if
                            type(entInTable.ix[0, col]) != type(None) and entInTable.ix[:, col].str.contains(qEntity,
                                                                                                            case=False).all()]
                if (len(entCol) > 0):
                    entCol = entCol[0]
                tables2search.append({'table': tbl, 'entCol': entCol})
        
        progress_bar.value += 2

        # for each table, find the time window to query on
        for tbl in tables2search:
            tbl['minTimestamp'], tbl['delta'], tbl['maxTimestamp'], tbl['longMinTimestamp'] = self.get_timewindow(qEntity, qTimestamp, tbl['entCol'], tbl['table'])

        progress_bar.value += 1

        # identify all the categorical columns per table on which we will find anomalies
        categoricalCols = []
        for tbl in tables2search:
            dfCols = self.query_loganalytics(KqlLibrary.IsCatColumn(tbl['table']))

            for col in dfCols.ColumnName:
                dfIsCat = self.query_loganalytics(KqlLibrary.IsCatHeuristic(tbl['table'], col))

                if (dfIsCat.shape[0] > 0):
                    catColInfo = copy.deepcopy(tbl)
                    catColInfo['col'] = col
                    categoricalCols.append(catColInfo)

        progress_bar.value += 2

        anomaliesList = []
        for colInfo in categoricalCols:
            maxTimestamp = colInfo['maxTimestamp'].strftime('%Y-%m-%dT%H:%M:%S.%f')
            longMinTimestamp = colInfo['longMinTimestamp'].strftime('%Y-%m-%dT%H:%M:%S.%f')

            curAnomalies = self.query_loganalytics(KqlLibrary.TimeSeriesAnomalyDetection(
                colInfo['table'],
                colInfo['col'],
                colInfo['entCol'],
                qEntity,
                longMinTimestamp,
                maxTimestamp,
                qTimestamp,
                colInfo['delta']))

            anomaliesList.append(curAnomalies)

        progress_bar.value += 2

        if (len(anomaliesList) > 0):
            anomalies = pd.concat(anomaliesList,axis=0)
        else:
            anomalies = pd.DataFrame()

        progress_bar.value += 1
        queries = self.construct_related_queries(anomalies)
        progress_bar.close()
        self.anomaly = str(anomalies.to_json(orient='records'))

        return anomalies, queries

    def is_result_true_positive(self, button):
        val = self.is_tp.value
        if val:
            result = self.logger.IsResultTruePositive('AnomalyLookup', val, self.anomaly)
            if result == True: 
                print('saved')

    def ask_is_entity_compromised(self):
        label_tp = widgets.Label(value='Is this entity compromised?')
        self.is_tp = widgets.RadioButtons( options=['Yes', 'No'], value=None, description='', disabled=False)
        save_tp = widgets.Button(description='Save', disabled=False, style=AnomalyLookupViewHelper.define_button_style(), layout=AnomalyLookupViewHelper.define_button_layout(), icon='save')
        save_tp.on_click(self.is_result_true_positive)
        display(label_tp)
        display(self.is_tp)
        display(save_tp)