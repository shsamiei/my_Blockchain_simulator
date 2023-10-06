import random
import time
import simpy
import logging
import copy
import json
import numpy as np
import pandas as pd
from transactions import Transaction
from blocks import Block
from network_state_graph import network_creator,csv_loader
from monitor import creater_logger

MINING_TIME= 2
BLOCKSIZE= 5
txpool_SIZE= 10
BLOCKTIME = 20
curr = time.ctime()
MESSAGE_COUNT=0
max_latency=5
BLOCKID= 99900

class node():

    def __init__(self, node_id):
        self.node_id = node_id
        self.env = env
        self.txpool = []
        self.pendingpool = []
        self.block_gas_limit = config['block_gas_limit'] 
        self.block_list= []
        self.current_gas=0
        self.current_size=0
        self.known_blocks=[]
        self.known_tx=[]
        self.prev_hash=0
        self.prev_block=99900
        self.sealer_flag=0
        logger.debug('%d,%d, generated, node, -'%(env.now,self.nodeID))
        

    def add_trx(self, trx):
        self.txpool.append(trx)
        self.known_tx.append(trx.id)
        self.broadcast(trx, self.node_id, 0, 0)


    def receiver(self, data, type, sender):
        global MESSAGE_COUNT
        MESSAGE_COUNT-= 1
        if type==0 and (data.id not in self.known_tx):
            self.txpool.append(data)
            self.known_tx.append(data.id)
            logger.debug("%d,%d,received,transaction,%d "%(self.env.now,self.nodeID,data.id))
            self.broadcast(data, self.node_id, 0, sender)
        elif type==1 and (data.id not in self.known_blocks):
            self.intr_data= data
            self.known_blocks.append(data.id)
            self.broadcaster(data,self.nodeID,1,sent_by)
            logger.debug("%d,%d, received, block, %d"%(self.env.now,self.nodeID,data.id))
            self.receive_block()

    def broadcast(self, data, node_id, type, sender):
        print("Broadcasting....Broadcasting.....")
        yield env.timeout(1)
        global MESSAGE_COUNT
        def propagation(delay,each,data,type): 
            yield self.env.timeout(delay)
            each.receiver(data,type,nodeID)
        logger.debug("%d, %d, broadcasting, data, %d"%(env.now,self.nodeID,data.id))
        for each in node_map:
            if (each.nodeID != self.nodeID) and (each.nodeID != sent_by):                
                latency = node_network.loc[self.nodeID,each.nodeID]
                if latency!=0:    
                    MESSAGE_COUNT +=1
                    self.env.process(propagation(latency,each,data,type))



    def create_block(self):
        yield env.timeout(1)
        print("Strating Creating ... \n")  
        if len(self.txpool) != 0:
            for each_tx in self.txpool:
                self.current_gas += each_tx.gas
                self.current_size+= each_tx.size
                if self.current_gas<self.block_gas_limit:
                    self.pendingpool.append(self.txpool.pop(0))
                else:
                    break 
        global BLOCKID
        BLOCKID+=1
        self.prev_block +=1
        block = Block(self.current_size,self.prev_block,self.pendingpool,self.nodeID,self.prev_hash)
        self.prev_hash = block.hash
        print('%d, %d, Created, block, %d,%d'%(env.now,self.nodeID,block.id,block.size))
        logger.debug('%d, %d, Created, block,%d,%d'%(env.now,self.nodeID,block.id,block.size))
        print("hash of block is %s"%block.hash)
        self.block_list.insert(0,block)
        block_stability_logger.info("%s,%d,%d,created,%d"%(env.now,self.nodeID,block.id,block.size))
        logger.info("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
        self.known_blocks.append(block.id)
        import ipdb; ipdb.set_trace()
        self.broadcaster(block,self.nodeID,1,0)
        self.current_gas=0
        self.current_size=0
        self.pendingpool=[]


    def receive_block(self):
        print("%d,%d, interrupted, block, %d " %(env.now,self.nodeID,self.intr_data.id))
        logger.debug("%d,%d, interrupted, block, %d " %(env.now,self.nodeID,self.intr_data.id))      
        if self.prev_hash == self.intr_data.prev_hash:
            print("Previous hash match")
            block_set= set(self.intr_data.transactions)
            node_set = set(self.pendingpool)
            yield env.timeout(config['block_verify_time'])
            if block_set != node_set:
                block_extra= block_set-node_set
                node_extra= node_set-block_set
                self.known_tx.extend(list(block_extra))
                self.temp_trans = [each for each in self.pendingpool if each.id in node_extra]
                self.txpool.extend(self.temp_trans)
            self.block_list.insert(0,self.intr_data)
            self.prev_hash = self.intr_data.hash
            block_stability_logger.info("%s,%d,%d,received"%(env.now,self.nodeID,self.intr_data.id))
            logger.info("No of blocks in node %d is %d"%(self.nodeID,len(self.block_list)))
            self.pendingpool=[]
            self.intr_data=None
            self.current_gas=0
        else:
            print("%s,%d,%d,outofsync"%(env.now,self.nodeID,self.intr_data.id))
            print(self.prev_hash)
            print(self.intr_data.prev_hash)
            self.prev_hash = self.intr_data.hash
            block_stability_logger.info("%s,%d,%d,outofsync"%(env.now,self.nodeID,self.intr_data.id))


    def node_creater(self):
        global nodelist
        if config['load_csv']==1:
            global node_network
            node_network,nodelist=csv_loader()

        else:
            nodelist= random.sample(range(1000,1000+config['n_nodes']),config['n_nodes'])
            node_network=network_creator(nodelist,config['max_latency'])
        
        global node_map
        node_map = [nodes(each) for each in nodelist]

        if config['consensus']=="POW":
            n_sealer=config['POW']['sealer_number']
            sealer_nodes=np.random.choice(node_map,n_sealer,replace=False)
            for each in sealer_nodes:
                each.sealer_flag=1


    def trx_generator(self):
        global txID
        txID = 2300
        while True:
            TX_SIZE = random.gauss(config['mean_tx_size'],config['sd_tx_size'])
            TX_GAS = random.gauss(config['mean_tx_gas'],config['sd_tx_gas'])
            
            txID  += 1
            transaction = Transaction(TX_GAS,TX_SIZE,txID)
            node=100
            for i in node_map:
                if i.nodeID==node:
                    print("%d, %d, Appended, Transaction, %d"%(env.now,i.nodeID,txID))
                    logger.debug("%d, %d,Appended, Transaction, %d"%(env.now,i.nodeID,txID))
                    i.add_transaction(transaction)
            yield env.timeout(random.gauss(config['mean_tx_generation'],config['sd_tx_generation']))


    def monitoring(env):
        prev_tx = 2300
        prev_block = 99900
        avg_pending_tx= 0
        while True:
            yield env.timeout(10)
            message_count_logger.info("%d,%d"%(env.now,MESSAGE_COUNT))
            avg_tx= txID-prev_tx
            prev_tx=txID

            avg_block= BLOCKID-prev_block
            prev_block=BLOCKID
            block_creation_logger.info("%d,%d"%(env.now,avg_block))
            
            for each in node_map:
                avg_pending_tx+= len(each.pendingpool)
            average= avg_pending_tx
            pending_transaction_logger.info("%d,%d"%(env.now,average))        
            avg_pending_tx=0

            hash_list = set()
            len_list = set()
            for each in node_map:
                len_list.add(len(each.block_list))
                for block in each.block_list:
                    hash_list.add(block.hash)
                
            unique_block_logger.info("%d,%d"%(env.now,len(hash_list)))


    def POA(env):
         while True:
            sealer=random.choice(node_map)
            print("Selected %d as a sealer"%sealer.nodeID)
            yield env.timeout(150)
            env.process(sealer.create_block())

    if __name__== "__main__":

        with open('config/config.json') as json_data:
            config= json.load(json_data)
        env=simpy.Environment()
        message_count_logger,block_creation_logger,unique_block_logger,pending_transaction_logger,logger,block_stability_logger=creater_logger()
        start_time = time.time()
        node_generator(env)
        env.process(trans_generator(env))

        env.process(POA(env))
        env.run(until=config['sim_time'])
        elapsed_time = time.time() - start_time
        print("----------------------------------------------------")
        print("Simulation ended")
        logger.info("Simulation ended")
        print("Total Time taken %d:"%elapsed_time)



