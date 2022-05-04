# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from typing import Optional

from flask_appbuilder.security.sqla.models import User
from sqlalchemy.sql.sqltypes import String

from superset import ConnectorRegistry, db, security_manager
from superset.charts.commands.exceptions import (
    ChartAccessDeniedError,
    ChartNotFoundError,
)
from superset.charts.dao import ChartDAO
from superset.datasets.commands.exceptions import (
    DatasetAccessDeniedError,
    DatasetNotFoundError,
)
from superset.datasets.dao import DatasetDAO
from superset.views.base import is_user_admin
from superset.views.utils import is_owner


def check_dataset_access(datasource_id: int, datasource_type: str) -> Optional[bool]:
    if datasource_id:
        dataset = ConnectorRegistry.get_datasource(
            datasource_type=datasource_type,
            datasource_id=datasource_id,
            session=db.session,
        )
        if dataset:
            can_access_datasource = security_manager.can_access_datasource(dataset)
            if can_access_datasource:
                return True
            raise DatasetAccessDeniedError()
    raise DatasetNotFoundError()


def check_access(
    datasource_id: int, chart_id: Optional[int], actor: User, datasource_type: str
) -> Optional[bool]:
    check_dataset_access(datasource_id, datasource_type)
    if not chart_id:
        return True
    chart = ChartDAO.find_by_id(chart_id)
    if chart:
        can_access_chart = (
            is_user_admin()
            or is_owner(chart, actor)
            or security_manager.can_access("can_read", "Chart")
        )
        if can_access_chart:
            return True
        raise ChartAccessDeniedError()
    raise ChartNotFoundError()
