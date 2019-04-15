# -*- coding: utf-8 -*-

import KBEngine
from KBEDebug import *
import utility
import const
import random

class iRoomRules(object):

	def __init__(self):
		# 房间的牌堆
		self.tiles = []
		self.meld_dict = dict()

	def swapSeat(self, swap_list):
		random.shuffle(swap_list)
		for i in range(len(swap_list)):
			self.players_list[i] = self.origin_players_list[swap_list[i]]

		for i,p in enumerate(self.players_list):
			if p is not None:
				p.idx = i

	def setPrevailingWind(self):
		#圈风
		if self.player_num != 4:
			return
		minDearerNum = min(self.dealerNumList)
		self.prevailing_wind = const.WINDS[(self.prevailing_wind + 1 - const.WIND_EAST)%len(const.WINDS)] if minDearerNum >= 1 else self.prevailing_wind
		self.dealerNumList = [0] * self.player_num if minDearerNum >= 1 else self.dealerNumList
		self.dealerNumList[self.dealer_idx] += 1

	def setPlayerWind(self):
		if self.player_num != 4:
			return
		#位风
		for i,p in enumerate(self.players_list):
			if p is not None:
				p.wind = (self.player_num + i - self.dealer_idx)%self.player_num + const.WIND_EAST

	def initTiles(self):
		# 万 条 筒
		self.tiles = list(const.CHARACTER) * 4 + list(const.BAMBOO) * 4 + list(const.DOT) * 4
		# 东 西 南 北
		self.tiles += [const.WIND_EAST, const.WIND_SOUTH, const.WIND_WEST, const.WIND_NORTH] * 4
		# 中 发 白
		self.tiles += [const.DRAGON_RED, const.DRAGON_GREEN, const.DRAGON_WHITE] * 4
		# # 春 夏 秋 冬
		# self.tiles += [const.SEASON_SPRING, const.SEASON_SUMMER, const.SEASON_AUTUMN, const.SEASON_WINTER]
		# # 梅 兰 竹 菊
		# self.tiles += [const.FLOWER_PLUM, const.FLOWER_ORCHID, const.FLOWER_BAMBOO, const.FLOWER_CHRYSANTHEMUM]
		DEBUG_MSG("room:{},curround:{} init tiles:{}".format(self.roomID, self.current_round, self.tiles))
		self.shuffle_tiles()

	def shuffle_tiles(self):
		random.shuffle(self.tiles)
		DEBUG_MSG("room:{},curround:{} shuffle tiles:{}".format(self.roomID, self.current_round, self.tiles))

	def deal(self, prefabHandTiles, prefabTopList):
		""" 发牌 """
		if prefabHandTiles is not None:
			for i,p in enumerate(self.players_list):
				if p is not None and len(prefabHandTiles) >= 0:
					if len(prefabHandTiles[i]) >= 4:
						p.standTileList = prefabHandTiles[i][0:4]
					elif len(prefabHandTiles[i]) <4:
						p.standTileList = prefabHandTiles[i][0:len(prefabHandTiles[i])]
					p.tiles = prefabHandTiles[i] if len(prefabHandTiles[i]) <= const.INIT_TILE_NUMBER else prefabHandTiles[i][0:const.INIT_TILE_NUMBER]
			topList = prefabTopList if prefabTopList is not None else []
			allTiles = []
			for i, p in enumerate(self.players_list):
				if p is not None:
					allTiles.extend(p.tiles)
			allTiles.extend(topList)

			tile2NumDict = utility.getTile2NumDict(allTiles)
			warning_tiles = [t for t, num in tile2NumDict.items() if num > 4]
			if len(warning_tiles) > 0:
				WARNING_MSG("room:{},curround:{} prefab {} is larger than 4.".format(self.roomID, self.current_round,
																					 warning_tiles))
			for t in allTiles:
				if t in self.tiles:
					self.tiles.remove(t)
			for i in range(const.INIT_TILE_NUMBER):
				num = 0
				for j in range(self.player_num):
					p = self.players_list[j]
					if len(p.tiles) >= const.INIT_TILE_NUMBER:
						continue
					if len(p.standTileList) < 4:
						p.standTileList.append(self.tiles[num])
					p.tiles.append(self.tiles[num])
					num += 1
				self.tiles = self.tiles[num:]

			newTiles = topList
			newTiles.extend(self.tiles)
			self.tiles = newTiles
		else:
			for i in range(const.INIT_TILE_NUMBER):
				for j in range(self.player_num):
					p = self.players_list[j]
					p.tiles.append(self.tiles[j])
					if i <= 3:
						p.standTileList.append(self.tiles[j])
				self.tiles = self.tiles[self.player_num:]

		for i, p in enumerate(self.players_list):
			DEBUG_MSG("room:{},curround:{} idx:{} deal tiles:{}".format(self.roomID, self.current_round, i, p.tiles))
			DEBUG_MSG("room:{},curround:{} idx:{} deal standTileList:{}".format(self.roomID, self.current_round, i, p.standTileList))

	def kongWreath(self):
		""" 杠花 """
		for i in range(self.player_num):
			for j in range(len(self.players_list[i].tiles)-1, -1, -1):
				tile = self.players_list[i].tiles[j]
				if tile in const.SEASON or tile in const.FLOWER:
					del self.players_list[i].tiles[j]
					self.players_list[i].wreaths.append(tile)
					DEBUG_MSG("room:{},curround:{} kong wreath, idx:{},tile:{}".format(self.roomID, self.current_round, i, tile))

	def addWreath(self):
		""" 补花 """
		for i in range(self.player_num):
			while len(self.players_list[i].tiles) < const.INIT_TILE_NUMBER:
				if len(self.tiles) <= 0:
					break
				tile = self.tiles[0]
				self.tiles = self.tiles[1:]
				if tile in const.SEASON or tile in const.FLOWER:
					self.players_list[i].wreaths.append(tile)
					DEBUG_MSG("room:{},curround:{} add wreath, tile is wreath,idx:{},tile:{}".format(self.roomID, self.current_round, i, tile))
				else:
					self.players_list[i].tiles.append(tile)
					DEBUG_MSG("room:{},curround:{} add wreath, tile is not wreath, idx:{},tile:{}".format(self.roomID, self.current_round, i, tile))

	# def rollKingTile(self):
	# 	""" 财神 """
	# 	self.kingTiles = []
	# 	if self.king_num > 0:
	# 		for i in range(len(self.tiles)):
	# 			t = self.tiles[i]
	# 			if t not in const.SEASON and t not in const.FLOWER: #第一张非花牌
	# 				# 1-9为一圈 东南西北为一圈 中发白为一圈
	# 				self.kingTiles.append(t)
	# 				if self.king_num > 1:
	# 					for tup in (const.CHARACTER, const.BAMBOO, const.DOT, const.WINDS, const.DRAGONS):
	# 						if t in tup:
	# 							index = tup.index(t)
	# 							self.kingTiles.append(tup[(index + 1)%len(tup)])
	# 							break
	# 				del self.tiles[i]
	# 				break

	# 杭州麻将特殊处理
	def rollKingTile(self, prefabKingTiles):
		""" 财神 """
		self.kingTiles = []
		if prefabKingTiles is not None and len(prefabKingTiles) > 0:
			if self.king_num > 0:
				if self.king_mode == 0:  # 财神模式 固定白板
					if prefabKingTiles[0] in const.WINDS or prefabKingTiles[0] in const.DRAGONS:
						self.kingTiles.append(prefabKingTiles[0])
					else:
						self.kingTiles.append(const.DRAGON_WHITE)
				else:
					self.kingTiles.append(prefabKingTiles[0])
		else:
			if self.king_num > 0:
				if self.king_mode == 0: # 风耗子
					for i in range(len(self.tiles)):
						t = self.tiles[i]
						if t in const.WINDS or t in const.DRAGONS:
							self.kingTiles.append(t)
							# del self.tiles[i]
							break
				else: 					# 随机耗子
					for i in range(len(self.tiles)):
						t = self.tiles[i]
						if t not in const.SEASON and t not in const.FLOWER:
							self.kingTiles.append(t)
							# del self.tiles[i]
							break

	def tidy(self):
		""" 整理 """
		for i in range(self.player_num):
			self.players_list[i].tidy(self.kingTiles)

	def count_king_tile(self):
		for i in range(self.player_num):
			p = self.players_list[i]
			p.count_draw_king(p.tiles)

	def throwDice(self, idxList):
		diceList = [[0,0] for i in range(self.player_num)]
		for i in range(len(diceList)):
			if i in idxList:
				diceList[i][0] = random.randint(1, 6)
				diceList[i][1] = random.randint(1, 6)
		return diceList

	def getMaxDiceIdx(self, diceList):
		numList = [v[0] + v[1] for v in diceList]
		maxVal, maxIdx = max(numList), self.dealer_idx
		for i in range(self.dealer_idx, self.dealer_idx + self.player_num):
			idx = i%self.player_num
			if numList[idx] == maxVal:
				maxIdx = idx
				break
		return maxIdx, maxVal

	def drawLuckyTile(self):
		return []
		# luckyTileList = []
		# for i in range(self.lucky_num):
		# 	if len(self.tiles) > 0:
		# 		luckyTileList.append(self.tiles[0])
		# 		self.tiles = self.tiles[1:]
		# return luckyTileList

	def cal_lucky_tile_score(self, lucky_tiles, winIdx):
		pass

	def swapTileToTop(self, tile):
		if tile in self.tiles:
			tileIdx = self.tiles.index(tile)
			self.tiles[0], self.tiles[tileIdx] = self.tiles[tileIdx], self.tiles[0]

	def winCount(self):
		pass

	def canTenPai(self, handTiles):
		length = len(handTiles)
		if length % 3 != 2:
			return False

		result = []
		tryTuple = (const.CHARACTER, const.BAMBOO, const.DOT, const.WINDS, const.DRAGONS)
		tryList = []
		for tup in tryTuple:
			tryList += tup
		for tile in handTiles:
			handCopyTiles = list(handTiles)
			sorted(handCopyTiles)
			handCopyTiles.remove(tile)
			for t in tryList:
				tmp = list(handCopyTiles)
				tmp.append(t)
				sorted(tmp)
				if utility.isWinTile(tmp, self.kingTiles):
					result.append(t)
					return True
		return False
		# return result != []

	def is_op_times_limit(self, idx):
		"""吃碰杠次数限制"""
		# if self.three_job and (idx == self.dealer_idx or self.last_player_idx == self.dealer_idx): # 三摊 承包的模式 庄闲之间 无限制
		# 	return False
		# op_r = self.players_list[idx].op_r
		# include_op_list = [const.OP_CHOW, const.OP_PONG, const.OP_EXPOSED_KONG] if self.pong_useful else [const.OP_CHOW]
		# times = sum([1 for record in op_r if record[2] == self.last_player_idx and record[0] in include_op_list])
		# return times >= 2
		return False

	def is_op_kingTile_limit(self, idx):
		"""打财神后操作限制"""
		if self.discard_king_idx >= 0 and self.discard_king_idx != idx and self.reward == 1:
			return True
		return False

	def is_op_limit(self, idx):
		"""操作限制"""
		if self.is_op_times_limit(idx) or self.is_op_kingTile_limit(idx):
			return True
		return False

	def circleSameTileNum(self, idx, t):
		"""获取一圈内打出同一张牌的张数"""
		discard_num = 0
		for record in reversed(self.op_record):
			if record[1] == idx:
				break
			if record[0] == const.DISCARD_FORCE and record[3][0] == t:
				discard_num -= 1
			if record[0] == const.OP_DISCARD and record[3][0] == t:
				discard_num += 1
		return discard_num

	def can_cut_after_kong(self):
		return False

	def can_discard(self, idx, t):
		if self.is_op_kingTile_limit(idx):
			if t == self.players_list[idx].last_draw:
				return True
			return False
		return True

	def can_chow(self, idx, t):
		return False
		if self.is_op_limit(idx):
			return False
		if t in self.kingTiles:
			return False
		# 白板代替财神
		virtual_tile = self.kingTiles[0] if t == const.DRAGON_WHITE and len(self.kingTiles) > 0 else t
		if virtual_tile >= const.BOUNDARY:
			return False
		tiles = list(filter(lambda x:x not in self.kingTiles, self.players_list[idx].tiles))
		tiles = list(map(lambda x:self.kingTiles[0] if x == const.DRAGON_WHITE else x, tiles))
		MATCH = ((-2, -1), (-1, 1), (1, 2))
		for tup in MATCH:
			if all(val+virtual_tile in tiles for val in tup):
				return True
		return False

	def can_chow_list(self, idx, tile_list):
		chow_list = list(tile_list)
		# """ 能吃 """
		if self.is_op_limit(idx):
			return False
		if len(chow_list) != 3:
			return False
		if any(t in self.kingTiles for t in tile_list):
			return False
		virtual_chow_list = list(tile_list)
		virtual_chow_list = list(map(lambda x:self.kingTiles[0] if x == const.DRAGON_WHITE else x, virtual_chow_list))
		if any(t >= const.BOUNDARY for t in virtual_chow_list):
			return False
		tiles 		= list(filter(lambda x: x not in self.kingTiles, self.players_list[idx].tiles))
		tiles 		= list(map(lambda x:self.kingTiles[0] if x == const.DRAGON_WHITE else x, tiles))
		if virtual_chow_list[1] in tiles and virtual_chow_list[2] in tiles:
			sortLis = sorted(virtual_chow_list)
			if (sortLis[2] + sortLis[0])/2 == sortLis[1] and sortLis[2] - sortLis[0] == 2:
				return True
		return False

	def can_pong(self, idx, t):
		""" 能碰 """
		if self.is_op_kingTile_limit(idx):
			return False
		# if self.pong_useful and self.is_op_times_limit(idx):
		# 	return False

		if self.circleSameTileNum(idx, t) >= 2:
			return False
		standTileList = self.players_list[idx].standTileList
		if len(standTileList) == 1 and t in standTileList:
			return False
		tiles = self.players_list[idx].tiles
		# if t in self.kingTiles:
		# 	return False
		return sum([1 for i in tiles if i == t]) >= 2

	def can_exposed_kong(self, idx, t):
		""" 能明杠 """
		if self.is_op_kingTile_limit(idx):
			return False
		# if self.pong_useful and self.is_op_times_limit(idx):
		# 	return False

		# if t in self.kingTiles:
		# 	return False
		standTileList = self.players_list[idx].standTileList
		if len(standTileList) == 1 and t in standTileList:
			return False
		tiles = self.players_list[idx].tiles
		return tiles.count(t) == 3

	def can_continue_kong(self, idx, t):
		""" 能够补杠 """
		# if t in self.kingTiles:
		# 	return False
		standTileList = self.players_list[idx].standTileList
		if len(standTileList) == 1 and t in standTileList:
			return False
		# 判断补杠后是否会影响所胡的牌,如果有影响,就无法补杠
		# 补杠必定不会影响所胡的牌
		player = self.players_list[idx]
		for op in player.op_r:
			if op[0] == const.OP_PONG and op[1][0] == t:
				return True
		return False

	def can_concealed_kong(self, idx, t):
		""" 能暗杠 """
		# if t in self.kingTiles:
		# 	return False
		standTileList = self.players_list[idx].standTileList
		if len(standTileList) == 1 and t in standTileList:
			return False
		# 判断暗杠后是否会影响所胡的牌,如果有影响,就无法暗杠
		p = self.players_list[idx]
		# if p.state == const.DISCARD_FORCE:
		# 	if t not in p.tiles or p.tiles.count(t) != 4:
		# 		return False
			# p_tiles = list(p.tiles)
			# p_tiles.remove(t)
			# canWinTilesPre = self.getCanWinTiles(p_tiles, const.OP_DRAW_WIN, idx)
			# a_tiles = list(p.tiles)
			# a_tiles.remove(t)
			# a_tiles.remove(t)
			# a_tiles.remove(t)
			# a_tiles.remove(t)
			# canWinTilesAft = self.getCanWinTiles(a_tiles, const.OP_DRAW_WIN, idx)
			# DEBUG_MSG("room:{},curround:{} can_concealed_kong canWinTilesPre:{} canWinTilesAft:{}".format(self.roomID, self.current_round, canWinTilesPre, canWinTilesAft))
			# if canWinTilesPre != canWinTilesAft:
			# 	return False
		tiles = self.players_list[idx].tiles
		return tiles.count(t) == 4

	def can_kong_wreath(self, tiles, t):
		if t in tiles and (t in const.SEASON or t in const.FLOWER):
			return True
		return False

	def can_wreath_win(self, wreaths):
		if len(wreaths) == len(const.SEASON) + len(const.FLOWER):
			return True
		return False

	def can_change_discard_state(self, tiles, i, state):
		if state == const.DISCARD_FREE:
			return True
		elif state == const.DISCARD_FORCE:
			return self.canTenPai(tiles)

	def getNotifyOpList(self, idx, aid, tile):
		# notifyOpList 和 self.wait_op_info_list 必须同时操作
		# 数据结构：问询玩家，操作玩家，牌，操作类型，得分，结果，状态
		notifyOpList = [[] for i in range(self.player_num)]
		self.wait_op_info_list = []
		if self.players_list[idx].buckle == 1:
			return notifyOpList
		#胡
		if aid == const.OP_KONG_WREATH and self.can_wreath_win(self.players_list[idx].wreaths): # 8花胡
			opDict = {"idx":idx, "from":idx, "tileList":[tile,], "aid":const.OP_WREATH_WIN, "score":0, "result":[], "state":const.OP_STATE_WAIT}
			notifyOpList[idx].append(opDict)
			self.wait_op_info_list.append(opDict)
		elif aid == const.OP_EXPOSED_KONG: #直杠 抢杠胡
			wait_for_win_list = self.getKongWinList(idx, tile)
			self.wait_op_info_list.extend(wait_for_win_list)
			for i in range(len(wait_for_win_list)):
				dic = wait_for_win_list[i]
				notifyOpList[dic["idx"]].append(dic)
			# pass
		elif aid == const.OP_CONTINUE_KONG: #碰后接杠 抢杠胡
			wait_for_win_list = self.getKongWinList(idx, tile)
			self.wait_op_info_list.extend(wait_for_win_list)
			for i in range(len(wait_for_win_list)):
				dic = wait_for_win_list[i]
				notifyOpList[dic["idx"]].append(dic)
			# pass
		elif aid == const.OP_CONCEALED_KONG:
			pass
		elif aid == const.OP_DISCARD:
			#胡(放炮胡)
			wait_for_win_list = self.getGiveWinList(idx, tile)
			self.wait_op_info_list.extend(wait_for_win_list)
			for i in range(len(wait_for_win_list)):
				dic = wait_for_win_list[i]
				notifyOpList[dic["idx"]].append(dic)
			#杠 碰
			for i, p in enumerate(self.players_list):
				if p and i != idx:
					if self.can_exposed_kong(i, tile):
						# 判断明杠后是否会影响所胡的牌,如果有影响,就无法明杠
						if p.state == const.DISCARD_FORCE:
							pass
							# canWinTilesPre = self.getCanWinTiles(p.tiles, const.OP_DRAW_WIN, i)
							# p_tiles = list(p.tiles)
							# p_tiles.remove(tile)
							# p_tiles.remove(tile)
							# p_tiles.remove(tile)
							# canWinTilesAft = self.getCanWinTiles(p_tiles, const.OP_DRAW_WIN, i)
							# if canWinTilesPre == canWinTilesAft:
							# 	opDict = {"idx":i, "from":idx, "tileList":[tile,], "aid":const.OP_EXPOSED_KONG, "score":0, "result":[], "state":const.OP_STATE_WAIT}
							# 	self.wait_op_info_list.append(opDict)
							# 	notifyOpList[i].append(opDict)
						else:
							standTileListTemp = list(p.standTileList)
							standNum = standTileListTemp.count(tile)
							for j in range(standNum):
								standTileListTemp.remove(tile)
							if len(standTileListTemp) > 0:
								opDict = {"idx":i, "from":idx, "tileList":[tile,], "aid":const.OP_EXPOSED_KONG, "score":0, "result":[], "state":const.OP_STATE_WAIT}
								self.wait_op_info_list.append(opDict)
								notifyOpList[i].append(opDict)
					if self.can_pong(i, tile) and p.state != const.DISCARD_FORCE:
						standTileListTemp = list(p.standTileList)
						if p.tiles.count(tile) < 3:
							standNum = standTileListTemp.count(tile)
							for j in range(standNum):
								standTileListTemp.remove(tile)
						# standNum = self.standTileList.count(tile)
						# for i in range(standNum):
						# 	self.standTileList.remove(tile)
						if len(standTileListTemp) > 0:
							opDict = {"idx":i, "from":idx, "tileList":[tile,], "aid":const.OP_PONG, "score":0, "result":[], "state":const.OP_STATE_WAIT}
							self.wait_op_info_list.append(opDict)
							notifyOpList[i].append(opDict)
			#吃
			nextIdx = self.nextIdx
			# if self.can_chow(nextIdx, tile):
			# 	opDict = {"idx":nextIdx, "from":idx, "tileList":[tile,], "aid":const.OP_CHOW, "score":0, "result":[], "state":const.OP_STATE_WAIT}
			# 	self.wait_op_info_list.append(opDict)
			# 	notifyOpList[nextIdx].append(opDict)
		return notifyOpList


	# 抢杠胡 玩家列表
	def getKongWinList(self, idx, tile):
		wait_for_win_list = []
		for i in range(self.player_num - 1):
			ask_idx = (idx+i+1)%self.player_num
			p = self.players_list[ask_idx]
			tryTiles = list(p.tiles)
			tryTiles.append(tile)
			tryTiles = sorted(tryTiles)
			DEBUG_MSG("room:{},curround:{} getKongWinList {}".format(self.roomID, self.current_round, ask_idx))
			is_win, score, result = self.can_win(tryTiles, tile, const.OP_KONG_WIN, ask_idx)
			if is_win:
				wait_for_win_list.append({"idx":ask_idx, "from":idx, "tileList":[tile,], "aid":const.OP_KONG_WIN, "score":score, "result":result, "state":const.OP_STATE_WAIT})
		return wait_for_win_list

	# 放炮胡 玩家列表
	def getGiveWinList(self, idx, tile):
		wait_for_win_list = []
		# if self.win_mode == 0 or self.cur_dealer_mul < 3: # 放铳模式 庄三有效
		# 	return  wait_for_win_list
		for i in range(self.player_num - 1):
			ask_idx = (idx+i+1)%self.player_num
			# if ask_idx != self.dealer_idx and idx != self.dealer_idx: # 庄闲放铳
			# 	continue
			p = self.players_list[ask_idx]
			tryTiles = list(p.tiles)
			tryTiles.append(tile)
			tryTiles = sorted(tryTiles)
			DEBUG_MSG("room:{},curround:{} getGiveWinList {} tile {}".format(self.roomID, self.current_round, ask_idx, tile))
			is_win, score, result = self.can_win(tryTiles, tile, const.OP_GIVE_WIN, ask_idx)
			if is_win:
				wait_for_win_list.append({"idx":ask_idx, "from":idx, "tileList":[tile,], "aid":const.OP_GIVE_WIN, "score":score, "result":result, "state":const.OP_STATE_WAIT})
		return wait_for_win_list

	def getCanWinTiles(self, handTiles, win_op, idx):
		handCopyTiles = list(handTiles)
		handCopyTiles = sorted(handCopyTiles)
		kings, handTilesButKing = utility.classifyKingTiles(handCopyTiles, self.kingTiles)
		kingTilesNum = len(kings)
		allTiles = const.CHARACTER + const.BAMBOO + const.DOT + const.WINDS + const.DRAGONS
		canWinTiles = []
		for tile in allTiles:
			handCopyTiles.append(tile)
			is_win, _, _ = self.can_win(handCopyTiles, tile, win_op, idx)
			if is_win:
				canWinTiles.append(tile)
			handCopyTiles.pop()
		DEBUG_MSG("room:{},curround:{} getCanWinTiles idx:{} canWinTiles:{}".format(self.roomID, self.current_round, idx, canWinTiles))
		return canWinTiles


	def is_win_limit(self, finalTile, win_op):
		DEBUG_MSG("room:{},curround:{} is_win_limit finalTile:{} win_op:{}".format(self.roomID, self.current_round, finalTile, win_op))
		if finalTile in self.kingTiles:
			if win_op != const.OP_DRAW_WIN:
				return False
			return True
		# 风字牌能胡
		if finalTile > const.BOUNDARY:
			return True
		# 12不能胡
		if finalTile % 10 <= 2:
			return False
		# 345只能自摸
		if finalTile % 10 >= 3 and finalTile % 10 <= 5 and win_op != const.OP_DRAW_WIN:
			return False
		return True

	def can_win(self, handTiles, finalTile, win_op, idx):
		#"""0自摸 1点炮 2抢杠 3明杠 4暗杠 5庄家 6边张 7砍张 8吊将 9缺门 10清一色 11一条龙 12清龙"""
		result_list = [0] * 13
		base_score = 1
		p = self.players_list[idx]
		if p.state == const.DISCARD_FREE:
			DEBUG_MSG("room:{},curround:{} 0 handTiles:{} finalTile:{} win_op:{} idx:{}".format(self.roomID, self.current_round, handTiles, finalTile, win_op, idx))
			return False, base_score, result_list
		if len(handTiles) % 3 != 2:
			DEBUG_MSG("room:{},curround:{} 1 handTiles:{} finalTile:{} win_op:{} idx:{}".format(self.roomID, self.current_round, handTiles, finalTile, win_op, idx))
			return False, base_score, result_list
		if win_op == const.OP_WREATH_WIN:
			DEBUG_MSG("room:{},curround:{} 2 handTiles:{} finalTile:{} win_op:{} idx:{}".format(self.roomID, self.current_round, handTiles, finalTile, win_op, idx))
			return False, base_score, result_list

		# DEBUG_MSG("room:{},curround:{} handTiles:{} finalTile:{} win_op:{} idx:{}".format(self.roomID, self.current_round, handTiles, finalTile, win_op, idx))

		handCopyTiles = list(handTiles)
		handCopyTiles = sorted(handCopyTiles)
		kings, handTilesButKing = utility.classifyKingTiles(handCopyTiles, self.kingTiles)
		kingTilesNum = len(kings)
		uptiles = p.upTiles

		#3N2
		if kingTilesNum <= 0: 	#无财神(只要满足能胡就可以胡)
			if utility.meld_with_pair_need_num(handTilesButKing) <= kingTilesNum:
				result_list[0] = 1 if win_op == const.OP_DRAW_WIN else 0
				# result_list[1] = 1 if win_op == const.OP_GIVE_WIN else 0
				# result_list[2] = 1 if win_op == const.OP_KONG_WIN else 0
				exposed_kong_num = sum([1 for op in p.op_r if op[0] == const.OP_EXPOSED_KONG])
				concealed_kong_num = sum([1 for op in p.op_r if op[0] == const.OP_CONCEALED_KONG])
				continue_kong_num = sum([1 for op in p.op_r if op[0] == const.OP_CONTINUE_KONG])
				if exposed_kong_num > 0 or continue_kong_num > 0: # 明杠
					result_list[3] = 1
				if concealed_kong_num > 0: # 暗杠
					result_list[4] = 1
				if p.idx == self.dealer_idx: # 庄家
					result_list[5] = 1
					base_score += 1
				result_list[6], result_list[7], result_list[8] = utility.checkIsEdgeMidSingle(handTilesButKing, finalTile)
				if len(p.canWinTiles) != 1:
					result_list[6] = 0
					result_list[7] = 0
					result_list[8] = 0
				if result_list[6] == 1 or result_list[7] == 1 or result_list[8] == 1: # 边张 砍张 吊将
					base_score += 1
				colorType = utility.getTileColorType(handTilesButKing, uptiles)
				if colorType == const.LACK_DOOR: # 缺门
					result_list[9] = 1
					base_score += 1
				if self.same_suit_mode == 1 and colorType == const.SAME_SUIT: # 清一色
					result_list[10] = 1
					base_score += 10
				if utility.checkIsOneDragon(handTilesButKing): # 一条龙
					result_list[11] = 1
					base_score += 10
				if self.same_suit_loong == 1 and result_list[10] == 1 and result_list[11] == 1: # 清龙
					result_list[12] = 1
				DEBUG_MSG("room:{},curround:{} 3N2 result_list:{}".format(self.roomID, self.current_round, result_list))
				return True , (base_score * [2 if result_list[0] == 1 else 1][0]), result_list
			DEBUG_MSG("room:{},curround:{} 3 handTiles:{} finalTile:{} win_op:{} idx:{}".format(self.roomID, self.current_round, handTiles, finalTile, win_op, idx))
			return False, base_score, result_list
		# else:					#有财神
		# 	if utility.winWith3N2NeedKing(handTilesButKing) <= kingTilesNum:
		# 		result_list[0] = 1
		# 		DEBUG_MSG("room:{},curround:{} 3N win_op:{} finalTile:{}".format(self.roomID, self.current_round, win_op, finalTile))
		# 		# if self.is_win_limit(finalTile, win_op) == False:
		# 		# 	return False , base_score, result_list
		# 		isMouseGeneral = utility.isMouseGeneral(handTiles, handTilesButKing, kingTilesNum, self.kingTiles, finalTile)
		# 		if isMouseGeneral and win_op != const.OP_DRAW_WIN:
		# 			DEBUG_MSG("room:{},curround:{} 3N win_op:{} isMouseGeneral:{}".format(self.roomID, self.current_round, win_op, isMouseGeneral))
		# 			return False , base_score, result_list
		# 		return True , base_score * utility.multiplyCalc(self.game_mode, win_op, result_list), result_list
		# 	DEBUG_MSG("room:{},curround:{} 4 handTiles:{} finalTile:{} win_op:{} idx:{}".format(self.roomID, self.current_round, handTiles, finalTile, win_op, idx))
		# 	return False, base_score, result_list

	def cal_win_score(self, idx, fromIdx, score, tile, aid, result):
		# 胡牌算分
		from_player = self.players_list[fromIdx]
		win_player = self.players_list[idx]
		if from_player.state == const.DISCARD_FREE:
			from_player.add_score(-score * 3)
			win_player.add_score(score * 3)
			if aid == const.OP_GIVE_WIN or aid == const.OP_KONG_WIN:
				result[1] = 1
				from_player.add_score(-1)
				win_player.add_score(1)
			if idx != self.dealer_idx:
				if aid == const.OP_DRAW_WIN:
					from_player.add_score(-2)
					win_player.add_score(2)
				else:
					from_player.add_score(-1)
					win_player.add_score(1)
		elif from_player.state == const.DISCARD_FORCE:
			for i, p in enumerate(self.players_list):
				if p and i != idx:
					p.add_score(-score)
				elif p and i == idx:
					p.add_score(score * 3)
			if idx != self.dealer_idx:
				if aid == const.OP_DRAW_WIN:
					self.players_list[self.dealer_idx].add_score(-2)
					win_player.add_score(2)
				else:
					self.players_list[self.dealer_idx].add_score(-1)
					win_player.add_score(1)
		for i, p in enumerate(self.players_list):
			if p and i != idx:
				if from_player.state == const.DISCARD_FREE:
					from_player.add_score(win_player.kong_score_list[i])
				elif from_player.state == const.DISCARD_FORCE:
					p.add_score(win_player.kong_score_list[i])
			elif p and i == idx:
				p.add_score(win_player.kong_score_list[i])


	def cal_score(self, idx, fromIdx, aid, score, tile = None, result = []):
		# 算分
		player = self.players_list[idx]
		if aid == const.OP_EXPOSED_KONG:
			if self.players_list[fromIdx].state == const.DISCARD_FREE:
				player.kong_score_list[fromIdx] -= score * 3
				player.kong_score_list[idx] += score * 3
			elif self.players_list[fromIdx].state == const.DISCARD_FORCE:
				for i, p in enumerate(self.players_list):
					if p and i != idx:
						player.kong_score_list[i] -= score
					elif p and i == idx:
						player.kong_score_list[i] += score * 3
		elif aid == const.OP_CONCEALED_KONG or aid == const.OP_CONTINUE_KONG:
			for i, p in enumerate(self.players_list):
				if p and i != idx:
					player.kong_score_list[i] -= score
				elif p and i == idx:
					player.kong_score_list[i] += score * 3
		elif aid == const.OP_DRAW_WIN: # 自摸胡
			DEBUG_MSG("room:{0},curround:{1} OP_DRAW_WIN==>idx:{2}".format(self.roomID, self.current_round, idx))
			self.cal_win_score(idx, fromIdx, score, tile, aid, result)
		elif aid == const.OP_KONG_WIN: # 抢杠胡跟放炮胡一样
			DEBUG_MSG("room:{0},curround:{1} OP_KONG_WIN==>idx:{2}]".format(self.roomID, self.current_round, idx))
			self.cal_win_score(idx, fromIdx, score, tile, aid, result)
		elif aid == const.OP_GIVE_WIN: # 放炮胡
			DEBUG_MSG("room:{0},curround:{1} OP_GIVE_WIN==>idx:{2}]".format(self.roomID, self.current_round, idx))
			self.cal_win_score(idx, fromIdx, score, tile, aid, result)
		elif aid == const.OP_WREATH_WIN:
			pass