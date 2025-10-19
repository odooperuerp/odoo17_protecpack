-- disable niubiz payment provider
UPDATE payment_provider
   SET niubiz_user = 'integraciones.visanet@necomplus.com',
       niubiz_password = 'd5e7nk$M',
       niubiz_pw_merchant_id_pen = '341198214',
       niubiz_pw_merchant_id_usd = '456879853',
       niubiz_tk_merchant_id_pen = '342062522',
       niubiz_tk_merchant_id_usd = '342062522',
       niubiz_merchant_id_recurrent = '342062522',
       niubiz_confirmation_auto = False,
       niubiz_liquidation_auto = True;
