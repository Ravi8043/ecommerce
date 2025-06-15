import stripe
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from .models import Payment
from products.models import Order, OrderItem  # use your existing order/orderitems

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def create_checkout_session(self, request):
        # Get user's active order (assuming pending means unpaid)
        try:
            order = Order.objects.get(user=request.user, status='pending')
        except Order.DoesNotExist:
            return Response({"error": "No active order found."}, status=400)

        # Calculate total price from order items
        order_items = OrderItem.objects.filter(order=order)
        total_amount = sum(item.price * item.quantity for item in order_items)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Order #{order.user.username}",
                        },
                        "unit_amount": int(total_amount * 100),  # Stripe expects amount in cents
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url=settings.FRONTEND_URL + "/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=settings.FRONTEND_URL + "/cancel",
                customer_email=request.user.email,
            )

            # Save payment session
            Payment.objects.create(
                user=request.user,
                order=order,
                stripe_session_id=checkout_session.id,
                amount=total_amount,
            )

            return Response({"checkout_session_url": checkout_session.url})

        except Exception as e:
            return Response({"error": str(e)}, status=500)

