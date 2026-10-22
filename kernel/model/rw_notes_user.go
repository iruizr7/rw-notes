package model

import (
	"github.com/88250/gulu"
	"github.com/siyuan-note/siyuan/kernel/conf"
	"github.com/siyuan-note/siyuan/kernel/util"
)

// GetRWNotesLocalUser preserves the fork's local entitlement response until
// RW Notes organization identity replaces the inherited vendor account model.
func GetRWNotesLocalUser() *conf.User {
	cloudAccountMu.Lock()
	defer cloudAccountMu.Unlock()
	user := &conf.User{
		UserId:                          "0",
		UserName:                        "_",
		UserAvatarURL:                   "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
		UserHomeBImgURL:                 "",
		UserTitles:                      []*conf.UserTitle{},
		UserIntro:                       "",
		UserNickname:                    "",
		UserCreateTime:                  "29991231 00:00:00",
		UserSiYuanProExpireTime:         -1,
		UserToken:                       "token",
		UserTokenExpireTime:             "32503593600",
		UserSiYuanRepoSize:              0,
		UserSiYuanPointExchangeRepoSize: 0,
		UserSiYuanAssetSize:             0,
		UserTrafficUpload:               0,
		UserTrafficDownload:             0,
		UserTrafficAPIGet:               0,
		UserTrafficAPIPut:               0,
		UserTrafficTime:                 0,
		UserSiYuanSubscriptionPlan:      0,
		UserSiYuanSubscriptionStatus:    0,
		UserSiYuanSubscriptionType:      1,
		UserSiYuanOneTimePayStatus:      1,
	}

	Conf.SetUser(user)
	data, _ := gulu.JSON.MarshalJSON(user)
	Conf.UserData = util.AESEncrypt(string(data))
	Conf.Save()

	return user
}
