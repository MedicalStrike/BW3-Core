#!/usr/bin/python
# -*- coding: utf-8 -*-
r"""!
    ____  ____  ______       __      __       __       _____
   / __ )/ __ \/ ___/ |     / /___ _/ /______/ /_     |__  /
  / __  / / / /\__ \| | /| / / __ `/ __/ ___/ __ \     /_ <
 / /_/ / /_/ /___/ /| |/ |/ / /_/ / /_/ /__/ / / /   ___/ /
/_____/\____//____/ |__/|__/\__,_/\__/\___/_/ /_/   /____/
                German BOS Information Script
                     by Bastian Schroll

@file:        divera.py
@date:        16.01.2022
@author:      Lars Gremme
@description: Divera247 Plugin
"""
import logging
from plugin.pluginBase import PluginBase

# ###################### #
# Custom plugin includes #
import asyncio
from aiohttp import ClientSession
# ###################### #

logging.debug("- %s loaded", __name__)


class BoswatchPlugin(PluginBase):
    r"""!Description of the Plugin"""
    def __init__(self, config):
        r"""!Do not change anything here!"""
        super().__init__(__name__, config)  # you can access the config class on 'self.config'

    def fms(self, bwPacket):
        r"""!Called on FMS alarm

        @param bwPacket: bwPacket instance
        Remove if not implemented"""
        fms_data = self.config.get("fms")
        apicall = {
            "vehicle_ric": self.parseWildcards(fms_data.get("vehicle", default="")),
            "status_id": bwPacket.get("status"),
            "status_note": bwPacket.get("directionText"),
            "title": self.parseWildcards(fms_data.get("title", default="{FMS}")),
            "text": self.parseWildcards(fms_data.get("message", default="{FMS}")),
            "priority": fms_data.get("priority", default="false"),
        }
        apipath = "/api/fms"
        self._makeRequests(apipath, apicall)

    def pocsag(self, bwPacket):
        r"""!Called on POCSAG alarm

        @param bwPacket: bwPacket instance
        Remove if not implemented"""
        poc_data = self.config.get("pocsag")
        apicall = {
            "title": self.parseWildcards(poc_data.get("title", default="{RIC}({SRIC})\n{MSG}")),
            "ric": self.parseWildcards(poc_data.get("ric", default="")),
            "text": self.parseWildcards(poc_data.get("message", default="{MSG}")),
            "priority": poc_data.get("priority", default="false"),
        }
        apipath = "/api/alarm"
        self._makeRequests(apipath, apicall)

    def zvei(self, bwPacket):
        r"""!Called on ZVEI alarm

        @param bwPacket: bwPacket instance
        Remove if not implemented"""
        zvei_data = self.config.get("zvei")
        apicall = {
            "title": self.parseWildcards(zvei_data.get("title", default="{TONE}")),
            "ric": self.parseWildcards(zvei_data.get("ric", default="{TONE}")),
            "text": self.parseWildcards(zvei_data.get("message", default="{TONE}")),
            "priority": zvei_data.get("priority", default="false"),
        }
        apipath = "/api/alarm"
        self._makeRequests(apipath, apicall)

    def msg(self, bwPacket):
        r"""!Called on MSG packet

        @param bwPacket: bwPacket instance
        Remove if not implemented"""
        msg_data = self.config.get("msg")
        apicall = {
            "title": self.parseWildcards(msg_data.get("title", default="{MSG}")),
            "ric": self.parseWildcards(msg_data.get("ric", default="")),
            "text": self.parseWildcards(msg_data.get("message", default="{MSG}")),
            "priority": msg_data.get("priority", default="false"),
        }
        apipath = "/api/alarm"
        self._makeRequests(apipath, apicall)

    def _makeRequests(self, apipath, apicall):
        """Parses wildcard urls and handles asynchronus requests

        @param urls: array of urls"""
        url = "https://www.divera247.com"
        request = url + apipath

        loop = asyncio.get_event_loop()

        future = asyncio.ensure_future(self._asyncRequests(request, apicall))
        loop.run_until_complete(future)

    async def _asyncRequests(self, url, apicall):
        """Handles asynchronus requests

        @param url: array of urls to send requests to"""
        tasks = []

        async with ClientSession() as session:
            logging.debug("Generated URL: [{}]".format(url))
            task = asyncio.ensure_future(self._fetch(url, apicall, session))
            tasks.append(task)

            responses = asyncio.gather(*tasks)
            await responses

    async def _fetch(self, url, apicall, session):
        """Fetches requests

        @param url: url

        @param session: Clientsession instance"""
        logging.debug("Post URL: [{}]".format(url))
        accesskey = "accesskey=" + self.config.get("accesskey", default="")
        async with session.request(method="post", url=url, json=apicall, params=accesskey) as response:
            logging.info("{} returned [{}]".format(response.url, response.status))
            return await response.read()
