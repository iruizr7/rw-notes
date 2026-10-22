package model

import (
	"testing"

	"github.com/siyuan-note/siyuan/kernel/conf"
	"github.com/siyuan-note/siyuan/kernel/util"
)

func TestRWNotesDisablesInheritedInstaller(t *testing.T) {
	previousConf, previousReadOnly, previousSkip := Conf, util.ReadOnly, skipInstallPkgPlatformCached
	Conf, util.ReadOnly, skipInstallPkgPlatformCached = NewAppConf(), true, 0
	Conf.System.Store(conf.NewSystem())
	t.Cleanup(func() {
		Conf, util.ReadOnly, skipInstallPkgPlatformCached = previousConf, previousReadOnly, previousSkip
	})
	if Conf.LoadSystem().DownloadInstallPkg {
		t.Fatal("new configuration enables upstream installer downloads")
	}
	Conf.System.Load().DownloadInstallPkg = true
	if !skipNewVerInstallPkg() || Conf.LoadSystem().DownloadInstallPkg {
		t.Fatal("inherited enabled download setting was not disabled")
	}
	if path := getNewVerInstallPkgPath(false); path != "" {
		t.Fatalf("upstream installer was offered: %s", path)
	}
}
