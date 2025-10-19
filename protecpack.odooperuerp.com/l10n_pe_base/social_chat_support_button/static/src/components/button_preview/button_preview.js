/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { evaluateExpr } from "@web/core/py_js/py";
import { getNextTabableElement, getPreviousTabableElement } from "@web/core/utils/ui";
import { usePosition } from "@web/core/position_hook";
import { getActiveHotkey } from "@web/core/hotkeys/hotkey_service";
import { shallowEqual } from "@web/core/utils/arrays";
import { roundDecimals } from "@web/core/utils/numbers";
import { _t } from "@web/core/l10n/translation";
import { useRecordObserver } from "@web/model/relational_model/utils";

import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { TagsList } from "@web/core/tags_list/tags_list";
import { useOpenMany2XRecord } from "@web/views/fields/relational_utils";
import { formatPercentage } from "@web/views/fields/formatters";

import { Record } from "@web/model/record";
import { Field } from "@web/views/fields/field";
import {
    Component,
    useEffect,
    useState,
    useRef,
    useExternalListener,
    onMounted,
    onWillStart,
    onPatched,
} from "@odoo/owl";

export class ButtonPreview extends Component {
    static template = "social_chat_support_button.ButtonPreview";
    static components = {
        TagsList,
        Record,
        Field,
    }
    static props = {
        ...standardFieldProps,
    }
    elRef = useRef("czm-chat-support");
    setup() {
        useRecordObserver(this.willUpdateRecord.bind(this));
        this.state = useState({ props: this.props});
        console.log(this.state)
        console.log(this.props)
        useEffect(() => {
            this.update_button_preview()
        }, ()=>[this.elRef,this.props.record._changes]);
    }

    update_button_preview(){
        $(this.elRef.el).empty()
        $(this.elRef.el).attr({class:""})
        $(this.elRef.el).czmChatSupport(this.props.record.data.json_for_csmChatSupport)
        console.log(this.props.record.data.json_for_csmChatSupport)
    }
    async willUpdateRecord(record) {
        console.log(record)
    }
}

export const buttonPreview = {
    component: ButtonPreview,
    supportedTypes: ["char", "text","jsonb"]
};

registry.category("fields").add("button_preview", buttonPreview);
