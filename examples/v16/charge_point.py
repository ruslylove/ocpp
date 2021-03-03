import asyncio
import logging

try:
    import websockets
except ModuleNotFoundError:
    print("This example relies on the 'websockets' package.")
    print("Please install it by running: ")
    print()
    print(" $ pip install websockets")
    import sys
    sys.exit(1)


from ocpp.v16 import call
from ocpp.routing import on
from ocpp.v16 import call_result
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus, AuthorizationStatus
from ocpp.v16.enums import ReservationStatus

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp):
    # BOOT NOTIFICATION
    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            charge_point_model="EVity-01",
            charge_point_vendor="IBS Corp."
        )

        response = await self.call(request)

        if response.status == RegistrationStatus.accepted:
            print("Connected to central system.")

    # AUTHORIZE
    async def send_authorize(self):
        request = call.AuthorizePayload(
            id_tag = "123456"
        )

        response = await self.call(request)

        if response.id_tag_info['status'] == AuthorizationStatus.accepted:
            print("It is authorized.")

    @on(Action.ReserveNow)
    def on_reserve_now(self, 
        connector_id: int,
        expiry_date: str,
        parent_id_tag: str,
        id_tag: str,
        reservation_id: int, 
        **kwargs):
        return call_result.ReserveNowPayload(
            status = ReservationStatus.accepted 
        )


async def main():
    async with websockets.connect(
        'ws://localhost:9000/CP_1',
        subprotocols=['ocpp1.6']
    ) as ws:

        cp = ChargePoint('CP_1', ws)

        await asyncio.gather(cp.start(), cp.send_boot_notification(),cp.send_authorize())


if __name__ == '__main__':
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
