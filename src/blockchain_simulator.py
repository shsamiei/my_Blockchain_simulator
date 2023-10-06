


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
        pass


    def trx_generator(self):
        pass

    def monitoring(env):
        pass


    def POA(env):
        pass

go





