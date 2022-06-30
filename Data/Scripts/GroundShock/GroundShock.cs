using System;
using System.Collections.Generic;
using System.Text;
using Sandbox.Common.ObjectBuilders;
using Sandbox.ModAPI;
using VRage.Game;
using VRage.Game.Components;
using VRage.ModAPI;
using VRage.ObjectBuilders;
using VRage.Utils;

namespace Klime.GroundShock
{
    [MyEntityComponentDescriptor(typeof(MyObjectBuilder_MotorSuspension), false)]
    public class GroundShock : MyGameLogicComponent
    {
        IMyMotorSuspension suspension;

        public override void Init(MyObjectBuilder_EntityBase objectBuilder)
        {
            suspension = Entity as IMyMotorSuspension;
            NeedsUpdate = MyEntityUpdateEnum.BEFORE_NEXT_FRAME;
        }

        public override void UpdateOnceBeforeFrame()
        {
            if (suspension.CubeGrid.Physics != null)
            {
                NeedsUpdate = MyEntityUpdateEnum.EACH_100TH_FRAME;
            }
        }

        public override void UpdateAfterSimulation100()
        {
            suspension.AirShockEnabled = false;
        }

        public override void Close()
        {
            
        }
    }
}