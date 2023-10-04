import sys
sys.path.append("../content/ballsortutils")

import asyncio
from control_factory import get_control_sim
from ch0_scenario import Ch0Scenario

async def sequence_concurrent():
    bc = get_control_sim(0)
    async with bc:
        await bc.set_scenario(Ch0Scenario())

        # green marble
        t1 = asyncio.create_task(bc.move_horizontally(1))
        t2 = asyncio.create_task(bc.move_vertically(4))            
        await t1
        await t2    
        await bc.close_claw()
        await bc.move_horizontally(-1)
        await bc.open_claw()
        
        # blue marble
        await bc.move_horizontally(2)
        await bc.close_claw()
        t3 = asyncio.create_task(bc.move_vertically(-1))
        t4 = asyncio.create_task(bc.move_horizontally(-2))
        await t3
        await t4
        await bc.open_claw()
        
        #blue marble
        t1 = asyncio.create_task(bc.move_horizontally(3))
        t2 = asyncio.create_task(bc.move_vertically(1))
        await t1
        await t2
        await bc.close_claw()
        t1 = asyncio.create_task(bc.move_horizontally(-3))
        t2 = asyncio.create_task(bc.move_vertically(-2))
        await t1
        await t2
        await bc.open_claw()

def main():
    asyncio.run(sequence_concurrent())

if __name__ == "__main__":
    import time
    s = time.perf_counter()
    main()
    elapsed = time.perf_counter() - s
    print(f"\n{__file__} executed in {elapsed:0.2f} seconds.")

