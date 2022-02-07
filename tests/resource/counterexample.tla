---------------------------- MODULE counterexample ----------------------------

EXTENDS main

(* Constant initialization state *)
ConstInit == TRUE

(* Initial state *)
State0 ==
  action = [name |-> "Null"]
    /\ chains
      = ("cosmoshub"
        :> [activeChannels |-> {},
          bank |->
            1 :> "cosmoshub" :> 0 @@ 2 :> "cosmoshub" :> 0 @@ "osmosis" :> 2
              @@ 0 :> "cosmoshub" :> 5,
          channel |-> [ x \in {} |-> x ],
          ics20 |->
            [channel |-> [ x \in {} |-> x ],
              escrow |-> [ x \in {} |-> x ],
              portId |-> "transfer"],
          id |-> "cosmoshub",
          localPackets |->
            [expired |-> {},
              list |-> [ x \in {} |-> x ],
              pending |-> {},
              success |-> {}],
          nextAccountId |-> 3,
          nextChannelId |-> 0,
          nextPacketId |-> 0,
          ports |-> {"transfer"},
          remotePackets |-> [ x \in {} |-> x ],
          supply |-> "cosmoshub" :> 5]
        @@ "osmosis"
          :> [activeChannels |-> {},
            bank |->
              1 :> "osmosis" :> 0 @@ 2 :> "osmosis" :> 0 @@ 0 :> "osmosis" :> 5,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "osmosis",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "osmosis" :> 5]
        @@ "ixo"
          :> [activeChannels |-> {},
            bank |-> 1 :> "ixo" :> 0 @@ 2 :> "ixo" :> 0 @@ 0 :> "ixo" :> 5,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "ixo",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "ixo" :> 5])
    /\ outcome = [name |-> "Success"]

(* Transition 0 to State1 *)
State1 ==
  action
      = [amount |-> 4,
        denom |-> "cosmoshub",
        name |-> "LocalTransfer",
        source |-> 0,
        target |-> 1]
    /\ chains
      = ("cosmoshub"
        :> [activeChannels |-> {},
          bank |->
            1 :> "cosmoshub" :> 4 @@ 2 :> "cosmoshub" :> 0
              @@ 0 :> "cosmoshub" :> 1,
          channel |-> [ x \in {} |-> x ],
          ics20 |->
            [channel |-> [ x \in {} |-> x ],
              escrow |-> [ x \in {} |-> x ],
              portId |-> "transfer"],
          id |-> "cosmoshub",
          localPackets |->
            [expired |-> {},
              list |-> [ x \in {} |-> x ],
              pending |-> {},
              success |-> {}],
          nextAccountId |-> 3,
          nextChannelId |-> 0,
          nextPacketId |-> 0,
          ports |-> {"transfer"},
          remotePackets |-> [ x \in {} |-> x ],
          supply |-> "cosmoshub" :> 5]
        @@ "osmosis"
          :> [activeChannels |-> {},
            bank |->
              1 :> "osmosis" :> 0 @@ 2 :> "osmosis" :> 0 @@ 0 :> "osmosis" :> 5,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "osmosis",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "osmosis" :> 5]
        @@ "ixo"
          :> [activeChannels |-> {},
            bank |-> 1 :> "ixo" :> 0 @@ 2 :> "ixo" :> 0 @@ 0 :> "ixo" :> 5,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "ixo",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "ixo" :> 5])
    /\ outcome = [name |-> "Success"]

(* Transition 1 to State2 *)
State2 ==
  action = [chains |-> { "cosmoshub", "osmosis" }, name |-> "CreateChannel"]
    /\ chains
      = ("cosmoshub"
        :> [activeChannels |-> {0},
          bank |->
            1 :> "cosmoshub" :> 4 @@ 2 :> "cosmoshub" :> 0
              @@ 0 :> "cosmoshub" :> 1
              @@ 3 :> [ x \in {} |-> x ],
          channel |->
            0
              :> [source |->
                  [chainId |-> "cosmoshub",
                    channelId |-> 0,
                    portId |-> "transfer"],
                target |->
                  [chainId |-> "osmosis",
                    channelId |-> 0,
                    portId |-> "transfer"]],
          ics20 |->
            [channel |-> "osmosis" :> 0 @@ "ixo" :> 0,
              escrow |-> 0 :> 3,
              portId |-> "transfer"],
          id |-> "cosmoshub",
          localPackets |->
            [expired |-> {},
              list |-> [ x \in {} |-> x ],
              pending |-> {},
              success |-> {}],
          nextAccountId |-> 4,
          nextChannelId |-> 1,
          nextPacketId |-> 0,
          ports |-> {"transfer"},
          remotePackets |-> 0 :> [ x \in {} |-> x ],
          supply |-> "cosmoshub" :> 5]
        @@ "osmosis"
          :> [activeChannels |-> {0},
            bank |->
              2 :> "osmosis" :> 0 @@ 0 :> "osmosis" :> 5
                @@ 3 :> [ x \in {} |-> x ]
                @@ 1 :> "osmosis" :> 0,
            channel |->
              0
                :> [source |->
                    [chainId |-> "osmosis",
                      channelId |-> 0,
                      portId |-> "transfer"],
                  target |->
                    [chainId |-> "cosmoshub",
                      channelId |-> 0,
                      portId |-> "transfer"]],
            ics20 |->
              [channel |-> "cosmoshub" :> 0,
                escrow |-> 0 :> 3,
                portId |-> "transfer"],
            id |-> "osmosis",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 4,
            nextChannelId |-> 1,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> 0 :> [ x \in {} |-> x ],
            supply |-> "osmosis" :> 5]
        @@ "ixo"
          :> [activeChannels |-> {},
            bank |-> 1 :> "ixo" :> 0 @@ 0 :> "ixo" :> 5 @@ 2 :> "ixo" :> 0,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "ixo",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "ixo" :> 5])
    /\ outcome = [name |-> "Success"]

(* Transition 3 to State3 *)
State3 ==
  action
      = [name |-> "IBCTransferSendPacket",
        packet |->
          [amount |-> 3,
            channel |->
              [source |->
                  [chainId |-> "cosmoshub",
                    channelId |-> 0,
                    portId |-> "transfer"],
                target |->
                  [chainId |-> "osmosis",
                    channelId |-> 0,
                    portId |-> "transfer"]],
            denom |-> "cosmoshub",
            from |-> 1,
            id |-> 0,
            to |-> 1]]
    /\ chains
      = ("cosmoshub"
        :> [activeChannels |-> {0},
          bank |->
            3 :> "cosmoshub" :> 3 @@ "$C$53512" :> 71 @@ "$C$53515" :> 72
              @@ 1 :> "cosmoshub" :> 1
              @@ 0 :> "cosmoshub" :> 1
              @@ 2 :> "cosmoshub" :> 0,
          channel |->
            0
              :> [source |->
                  [chainId |-> "cosmoshub",
                    channelId |-> 0,
                    portId |-> "transfer"],
                target |->
                  [chainId |-> "osmosis",
                    channelId |-> 0,
                    portId |-> "transfer"]],
          ics20 |->
            [channel |-> "osmosis" :> 0 @@ "ixo" :> 0,
              escrow |-> 0 :> 3,
              portId |-> "transfer"],
          id |-> "cosmoshub",
          localPackets |->
            [expired |-> {},
              list |->
                0
                  :> [amount |-> 3,
                    channel |->
                      [source |->
                          [chainId |-> "cosmoshub",
                            channelId |-> 0,
                            portId |-> "transfer"],
                        target |->
                          [chainId |-> "osmosis",
                            channelId |-> 0,
                            portId |-> "transfer"]],
                    denom |-> "cosmoshub",
                    from |-> 1,
                    id |-> 0,
                    to |-> 1],
              pending |-> {0},
              success |-> {}],
          nextAccountId |-> 4,
          nextChannelId |-> 1,
          nextPacketId |-> 1,
          ports |-> {"transfer"},
          remotePackets |-> 0 :> [ x \in {} |-> x ],
          supply |-> "cosmoshub" :> 5]
        @@ "osmosis"
          :> [activeChannels |-> {0},
            bank |->
              2 :> "osmosis" :> 0 @@ 0 :> "osmosis" :> 5
                @@ 3 :> [ x \in {} |-> x ]
                @@ 1 :> "osmosis" :> 0,
            channel |->
              0
                :> [source |->
                    [chainId |-> "osmosis",
                      channelId |-> 0,
                      portId |-> "transfer"],
                  target |->
                    [chainId |-> "cosmoshub",
                      channelId |-> 0,
                      portId |-> "transfer"]],
            ics20 |->
              [channel |-> "cosmoshub" :> 0,
                escrow |-> 0 :> 3,
                portId |-> "transfer"],
            id |-> "osmosis",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 4,
            nextChannelId |-> 1,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> 0 :> [ x \in {} |-> x ],
            supply |-> "osmosis" :> 5]
        @@ "ixo"
          :> [activeChannels |-> {},
            bank |-> 0 :> "ixo" :> 5 @@ 2 :> "ixo" :> 0 @@ 1 :> "ixo" :> 0,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "ixo",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "ixo" :> 5])
    /\ outcome = [name |-> "Success"]

(* Transition 4 to State4 *)
State4 ==
  action
      = [name |-> "IBCTransferReceivePacket",
        packet |->
          [amount |-> 3,
            channel |->
              [source |->
                  [chainId |-> "cosmoshub",
                    channelId |-> 0,
                    portId |-> "transfer"],
                target |->
                  [chainId |-> "osmosis",
                    channelId |-> 0,
                    portId |-> "transfer"]],
            denom |-> "cosmoshub",
            from |-> 1,
            id |-> 0,
            to |-> 1]]
    /\ chains
      = ("cosmoshub"
        :> [activeChannels |-> {0},
          bank |->
            2 :> "cosmoshub" :> 0 @@ 1 :> "cosmoshub" :> 1
              @@ 0 :> "cosmoshub" :> 1
              @@ 3
                :> "cosmoshub" :> 3 @@ "$C$109962" :> 71 @@ "$C$109965" :> 72
                  @@ "$C$109968" :> 72,
          channel |->
            0
              :> [source |->
                  [chainId |-> "cosmoshub",
                    channelId |-> 0,
                    portId |-> "transfer"],
                target |->
                  [chainId |-> "osmosis",
                    channelId |-> 0,
                    portId |-> "transfer"]],
          ics20 |->
            [channel |-> "osmosis" :> 0 @@ "ixo" :> 0,
              escrow |-> 0 :> 3,
              portId |-> "transfer"],
          id |-> "cosmoshub",
          localPackets |->
            [expired |-> {},
              list |->
                0
                  :> [amount |-> 3,
                    channel |->
                      [source |->
                          [chainId |-> "cosmoshub",
                            channelId |-> 0,
                            portId |-> "transfer"],
                        target |->
                          [chainId |-> "osmosis",
                            channelId |-> 0,
                            portId |-> "transfer"]],
                    denom |-> "cosmoshub",
                    from |-> 1,
                    id |-> 0,
                    to |-> 1],
              pending |-> {0},
              success |-> {}],
          nextAccountId |-> 4,
          nextChannelId |-> 1,
          nextPacketId |-> 1,
          ports |-> {"transfer"},
          remotePackets |-> 0 :> [ x \in {} |-> x ],
          supply |-> "cosmoshub" :> 5]
        @@ "osmosis"
          :> [activeChannels |-> {0},
            bank |->
              1 :> "osmosis" :> 0 @@ "cosmoshub" :> 3 @@ 2 :> "osmosis" :> 0
                @@ 3 :> [ x \in {} |-> x ]
                @@ 0 :> "osmosis" :> 5,
            channel |->
              0
                :> [source |->
                    [chainId |-> "osmosis",
                      channelId |-> 0,
                      portId |-> "transfer"],
                  target |->
                    [chainId |-> "cosmoshub",
                      channelId |-> 0,
                      portId |-> "transfer"]],
            ics20 |->
              [channel |-> "cosmoshub" :> 0,
                escrow |-> 0 :> 3,
                portId |-> "transfer"],
            id |-> "osmosis",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 4,
            nextChannelId |-> 1,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |->
              0
                :> 0
                  :> [amount |-> 3,
                    channel |->
                      [source |->
                          [chainId |-> "cosmoshub",
                            channelId |-> 0,
                            portId |-> "transfer"],
                        target |->
                          [chainId |-> "osmosis",
                            channelId |-> 0,
                            portId |-> "transfer"]],
                    denom |-> "cosmoshub",
                    from |-> 1,
                    id |-> 0,
                    to |-> 1],
            supply |-> "cosmoshub" :> 3 @@ "osmosis" :> 5]
        @@ "ixo"
          :> [activeChannels |-> {},
            bank |-> 0 :> "ixo" :> 5 @@ 1 :> "ixo" :> 0 @@ 2 :> "ixo" :> 0,
            channel |-> [ x \in {} |-> x ],
            ics20 |->
              [channel |-> [ x \in {} |-> x ],
                escrow |-> [ x \in {} |-> x ],
                portId |-> "transfer"],
            id |-> "ixo",
            localPackets |->
              [expired |-> {},
                list |-> [ x \in {} |-> x ],
                pending |-> {},
                success |-> {}],
            nextAccountId |-> 3,
            nextChannelId |-> 0,
            nextPacketId |-> 0,
            ports |-> {"transfer"},
            remotePackets |-> [ x \in {} |-> x ],
            supply |-> "ixo" :> 5])
    /\ outcome = [name |-> "Success"]

(* The following formula holds true in the last state and violates the invariant *)
InvariantViolation == action["name"] = "IBCTransferReceivePacket"

================================================================================
(* Created by Apalache on Mon Feb 07 12:58:16 CET 2022 *)
(* https://github.com/informalsystems/apalache *)
