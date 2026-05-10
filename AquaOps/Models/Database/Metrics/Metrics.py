
from __future__ imp or t an not ations 

from datetime imp or t datetime 
from typ in g imp or t Optional 

from sqlalchemy imp or t BigInteger , DateTime , Float , F or eignKey , Index , Str in g , func 
from sqlalchemy .or m imp or t Mapped , mapped_column 

from AquaOps .Models .Database .base imp or t Base 






class Sens or Read in g (Base ):
    """
    Time-series sensor read in gs.
    One row per sample. Compatible with TimescaleDB hypertable on rec or ded_at.
    """
__tablename__ ="sens or _read in gs"
__table_args__ =(
Index ("ix_sens or _read in gs_sens or _rec or ded","sens or _id","rec or ded_at"),
Index ("ix_sens or _read in gs_node_rec or ded","node_id","rec or ded_at"),
{"schema":"aquaops"},
)

id :Mapped [in t ]=mapped_column (BigInteger , primary_key =True , auto in crement =True )
rec or ded_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ), server_ def ault =func .now (), in dex =True )


node_id :Mapped [str ]=mapped_column (Str in g (100 ))
sens or _id :Mapped [str ]=mapped_column (Str in g (100 ))
sens or _type :Mapped [str ]=mapped_column (Str in g (100 ), def ault ="")


module_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
zone_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )



value :Mapped [float |None ]=mapped_column (Float , nullable =True )
value_str :Mapped [str |None ]=mapped_column (Str in g (255 ), nullable =True )
unit :Mapped [str ]=mapped_column (Str in g (50 ), def ault ="")






class DeviceEvent (Base ):
    """
    Rec or ds every command sent to a device and its outcome.
    Drives runtime track in g and audit logs.
    """
__tablename__ ="device_events"
__table_args__ =(
Index ("ix_device_events_device_rec or ded","device_id","rec or ded_at"),
{"schema":"aquaops"},
)

id :Mapped [in t ]=mapped_column (BigInteger , primary_key =True , auto in crement =True )
rec or ded_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ), server_ def ault =func .now (), in dex =True )


node_id :Mapped [str ]=mapped_column (Str in g (100 ))
device_id :Mapped [str ]=mapped_column (Str in g (100 ))
device_type :Mapped [str ]=mapped_column (Str in g (100 ), def ault ="")


module_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
zone_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
w or kflow_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )


command :Mapped [str ]=mapped_column (Str in g (100 ), def ault ="")
outcome :Mapped [str ]=mapped_column (Str in g (50 ), def ault ="ok")
not e :Mapped [str |None ]=mapped_column (Str in g (500 ), nullable =True )






class W or kflowExecution (Base ):
    """
    One row per w or kflow run (trigger → stop/timeout).
    Tracks duration and why it ended.
    """
__tablename__ ="w or kflow_executions"
__table_args__ =(
Index ("ix_w or kflow_exec_w or kflow_started","w or kflow_id","started_at"),
{"schema":"aquaops"},
)

id :Mapped [in t ]=mapped_column (BigInteger , primary_key =True , auto in crement =True )
started_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ), server_ def ault =func .now (), in dex =True )
ended_at :Mapped [datetime |None ]=mapped_column (DateTime (timezone =True ), nullable =True )


w or kflow_id :Mapped [str ]=mapped_column (Str in g (100 ))
zone_id :Mapped [str ]=mapped_column (Str in g (100 ))
module_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )


trigger_type :Mapped [str ]=mapped_column (Str in g (100 ), def ault ="")
trigger_value :Mapped [str |None ]=mapped_column (Str in g (255 ), nullable =True )



status :Mapped [str ]=mapped_column (Str in g (50 ), def ault ="runn in g")
stop_reason :Mapped [str |None ]=mapped_column (Str in g (500 ), nullable =True )


duration_seconds :Mapped [float |None ]=mapped_column (Float , nullable =True )






class SafetyEvent (Base ):
    """
    Fires whenever the safety eng in e takes an action (alert, pause, shutdown).
    """
__tablename__ ="safety_events"
__table_args__ =(
Index ("ix_safety_events_module_rec or ded","module_id","rec or ded_at"),
{"schema":"aquaops"},
)

id :Mapped [in t ]=mapped_column (BigInteger , primary_key =True , auto in crement =True )
rec or ded_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ), server_ def ault =func .now (), in dex =True )


module_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
zone_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
w or kflow_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
policy_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
rule_id :Mapped [str |None ]=mapped_column (Str in g (100 ), nullable =True )
rule_type :Mapped [str ]=mapped_column (Str in g (100 ), def ault ="")


action_taken :Mapped [str ]=mapped_column (Str in g (50 ), def ault ="")
detail :Mapped [str |None ]=mapped_column (Str in g (500 ), nullable =True )






class NodeHeartbeat (Base ):
    """
    Lightweight p in g table. One row per heartbeat received from a node.
    Used for liveness checks and latency track in g.
    """
__tablename__ ="node_heartbeats"
__table_args__ =(
Index ("ix_node_heartbeats_node_rec or ded","node_id","rec or ded_at"),
{"schema":"aquaops"},
)

id :Mapped [in t ]=mapped_column (BigInteger , primary_key =True , auto in crement =True )
rec or ded_at :Mapped [datetime ]=mapped_column (DateTime (timezone =True ), server_ def ault =func .now (), in dex =True )

node_id :Mapped [str ]=mapped_column (Str in g (100 ))

latency_ms :Mapped [float |None ]=mapped_column (Float , nullable =True )

signal :Mapped [float |None ]=mapped_column (Float , nullable =True )