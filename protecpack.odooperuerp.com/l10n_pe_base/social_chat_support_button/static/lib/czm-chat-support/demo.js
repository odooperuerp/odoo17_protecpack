(function ($) {

	'use strict';
	
	/* =======================================================
	BUTTON EXAMPLES
	======================================================= */

	$('#button_1_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-whatsapp"></i>', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});

	$('#button_1_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-telegram-plane"></i>', /* Image, Icon or SVG */
			backgroundColor: "#18A3E6", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://telegram.me/telegram", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});

	$('#button_1_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-facebook-messenger"></i>', /* Image, Icon or SVG */
			backgroundColor: "#0084ff", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "http://m.me/cizimmedya", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});

	$('#button_1_4').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-skype"></i>', /* Image, Icon or SVG */
			backgroundColor: "#00aff0", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "skype:live:.cid.7b29081175cf6980?chat", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});

	$('#button_1_5').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<i class="fas fa-life-ring"></i>', /* Image, Icon or SVG */
			backgroundColor: "#ff9d2d", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "mailto:support@cizimmedya.com", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});

	$('#button_1_6').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "transparent", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_1_7').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/2.svg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "transparent", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_1_8').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 1, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-whatsapp"></i>', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: false,
				monday: false,
				tuesday: false,
				wednesday: false,
				thursday: false,
				friday: false,
				saturday: false
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_2_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 2, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-whatsapp"></i>', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_2_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 2, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-telegram-plane"></i>', /* Image, Icon or SVG */
			backgroundColor: "#18A3E6", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://telegram.me/telegram", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_2_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 2, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/2.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#a857c5", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Custom Text Custom", /* Writing is required */
				description: "Custom Text", /* To remove, (description:false) */
				online: "Custom Text", /* To remove, (online:false) */
				offline: "Custom Text" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_3_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 3, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-whatsapp"></i>', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_3_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 3, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-facebook-messenger"></i>', /* Image, Icon or SVG */
			backgroundColor: "#0084ff", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "http://m.me/cizimmedya", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_3_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 3, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.svg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#ec4c4c", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Custom Text Custom", /* Writing is required */
				description: "Custom Text", /* To remove, (description:false) */
				online: "Custom Text", /* To remove, (online:false) */
				offline: "Custom Text" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_4_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 4, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-whatsapp"></i>', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_4_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 4, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-skype"></i>', /* Image, Icon or SVG */
			backgroundColor: "#00aff0", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "skype:live:.cid.7b29081175cf6980?chat", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_4_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 4, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/3.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#ff9d2d", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Custom Text Custom", /* Writing is required */
				description: "Custom Text", /* To remove, (description:false) */
				online: "Custom Text", /* To remove, (online:false) */
				offline: "Custom Text" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_5_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 5, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-whatsapp"></i>', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_5_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 5, /* Button style. Number between 1 and 7 */
			src: '<i class="fab fa-linkedin-in"></i>', /* Image, Icon or SVG */
			backgroundColor: "#0A66C2", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://tr.linkedin.com/company/cizimmedya", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_5_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 5, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#de6bcd", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Custom Text Custom", /* Writing is required */
				description: "Custom Text", /* To remove, (description:false) */
				online: "Custom Text", /* To remove, (online:false) */
				offline: "Custom Text" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_6_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 6, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_6_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 6, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/2.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#f05c94", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://www.instagram.com/cizimmedyatr/", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_6_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 6, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.svg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#09ccbf", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Custom Text Custom", /* Writing is required */
				description: "Custom Text", /* To remove, (description:false) */
				online: "Custom Text", /* To remove, (online:false) */
				offline: "Custom Text" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_7_1').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 7, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#10c379", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_7_2').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 7, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/2.jpg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#9e63ce", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Need help? Chat with us", /* Writing is required */
				description: "Customer Support", /* To remove, (description:false) */
				online: "I'm Online", /* To remove, (online:false) */
				offline: "I will be back soon" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://www.viber.com/", /* Writing is required */
				mobile: false /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});
	
	$('#button_7_3').czmChatSupport({
		/* Button Settings */
		button: {
			position: false, /* left, right or false. "position:false" does not pin to the left or right */
			style: 7, /* Button style. Number between 1 and 7 */
			src: '<img src="assets/img/person/1.svg" alt="">', /* Image, Icon or SVG */
			backgroundColor: "#36aee2", /* Html color code */
			effect: 1, /* Button effect. Number between 1 and 7 */
			notificationNumber: false, /* Custom text or false. To remove, (notificationNumber:false) */
			speechBubble: false, /* To remove, (speechBubble:false) */
			pulseEffect: false, /* To remove, (pulseEffect:false) */
			text: { /* For Button style larger than 1 */
				title: "Custom Text Custom", /* Writing is required */
				description: "Custom Text", /* To remove, (description:false) */
				online: "Custom Text", /* To remove, (online:false) */
				offline: "Custom Text" /* To remove, (offline:false) */
			},
			link: {
				desktop: "https://web.whatsapp.com/send?phone=905377323226&text=Hi", /* Writing is required */
				mobile: "https://wa.me/905377323226/?text=Hi" /* If it is hidden desktop link will be valid. To remove, (mobile:false) */
			},
			onlineDay: {
				/* Change the day you are offline like this. (sunday:false) */
				sunday: "00:00-23:59",
				monday: "00:00-23:59",
				tuesday: "00:00-23:59",
				wednesday: "00:00-23:59",
				thursday: "00:00-23:59",
				friday: "00:00-23:59",
				saturday: "00:00-23:59"
			}
		},

		/* Other Settings */
		sound: false, /* true (default sound), false or custom sound. Custom sound example, (sound:'assets/sound/notification.mp3') */
		changeBrowserTitle: false, /* Custom text or false. To remove, (changeBrowserTitle:false) */
		cookie: false, /* It does not show the speech bubble, notification number, pulse effect and automatic open popup again for the specified time. For example, do not show for 1 hour, (cookie:1) or to remove, (cookie:false) */
	});

	/* =======================================================
	SCROLL MOVE
	======================================================= */

	$('.scroll-move').click(function () {
		$('html, body').animate({
			scrollTop: $($(this).attr('href')).offset().top
		}, 500);
		return false;
	});

}(jQuery));
