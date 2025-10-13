/** @odoo-module **/
import publicWidget from "@web/legacy/js/public/public_widget";


publicWidget.registry.SocialChatSupportButton = publicWidget.Widget.extend({
    selector:"#social_chat_support_button",
    disabledInEditableMode:true,
    start: function  () {
        this.rpc = this.bindService("rpc");
        this.rpc("/get_social_chat_button",{website_id:parseInt(this.$el.data("website_id"))}).then((data) => {
            this.$el.empty();
            this.$el.czmChatSupport(data)
        })
        return this._super(...arguments);
    },
    destroy: function  () {
        return this._super(...arguments);
    }
})
