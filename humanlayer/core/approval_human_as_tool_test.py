from unittest.mock import Mock

from humanlayer import (
    AgentBackend,
    ContactChannel,
    HumanContact,
    HumanContactSpec,
    HumanContactStatus,
    HumanLayer,
    SlackContactChannel,
)
from humanlayer.core.protocol import AgentStore


def test_human_as_tool_generic() -> None:
    """
    test that we omit contact channel if none passed,
    and let the backend decide whether to use a default
    or reject the call
    """
    mock_backend = Mock(spec=AgentBackend)
    contacts = Mock(spec=AgentStore[HumanContact])
    mock_backend.contacts.return_value = contacts

    contacts.add.return_value = None

    hl = HumanLayer(
        backend=mock_backend,
        genid=lambda x: "generated-id",
        sleep=lambda x: None,
    )

    contacts.get.return_value = HumanContact(
        run_id="generated-id",
        call_id="generated-id",
        spec=HumanContactSpec(msg="what is your favorite color"),
        status=HumanContactStatus(response="magenta"),
    )

    ret = hl.human_as_tool()("what is your favorite color")

    assert ret == "magenta"

    contacts.add.assert_called_once_with(
        HumanContact(
            run_id="generated-id",
            call_id="generated-id",
            spec=HumanContactSpec(msg="what is your favorite color"),
        )
    )

    contacts.get.assert_called_once_with("generated-id")


def test_human_as_tool_instance_contact_channel() -> None:
    """
    test that we can pass in a contact channel in the
    HumanLayer constructor
    """
    mock_backend = Mock(spec=AgentBackend)
    contacts = Mock(spec=AgentStore[HumanContact])
    mock_backend.contacts.return_value = contacts

    contacts.add.return_value = None

    contact_channel = ContactChannel(
        slack=SlackContactChannel(
            channel_or_user_id="U8675309",
            context_about_channel_or_user="a dm with the librarian",
        )
    )

    hl = HumanLayer(
        backend=mock_backend,
        contact_channel=contact_channel,
        genid=lambda x: "generated-id",
        sleep=lambda x: None,
    )

    contacts.get.return_value = HumanContact(
        run_id="generated-id",
        call_id="generated-id",
        spec=HumanContactSpec(
            msg="what is your favorite color",
            channel=contact_channel,
        ),
        status=HumanContactStatus(response="magenta"),
    )

    tool = hl.human_as_tool()

    assert (
        tool.__name__
        == """
    contact_human_in_slack_in_a_dm_with_the_librarian
    """.strip()
    )

    assert (
        tool.__doc__
        == """
    Contact a human via slack and wait for a response in a dm with the librarian
    """.strip()
    )

    ret = tool("what is your favorite color")

    assert ret == "magenta"

    contacts.add.assert_called_once_with(
        HumanContact(
            run_id="generated-id",
            call_id="generated-id",
            spec=HumanContactSpec(
                msg="what is your favorite color",
                channel=contact_channel,
            ),
        )
    )

    contacts.get.assert_called_once_with("generated-id")

    pass


def test_human_as_tool_fn_contact_channel() -> None:
    """
    test that we can pass in a contact channel in the
    human_as_tool() method
    """
    mock_backend = Mock(spec=AgentBackend)
    contacts = Mock(spec=AgentStore[HumanContact])
    mock_backend.contacts.return_value = contacts

    contacts.add.return_value = None

    contact_channel = ContactChannel(
        slack=SlackContactChannel(
            channel_or_user_id="U8675309",
            context_about_channel_or_user="a dm with the librarian",
        )
    )

    hl = HumanLayer(
        backend=mock_backend,
        genid=lambda x: "generated-id",
        sleep=lambda x: None,
    )

    contacts.get.return_value = HumanContact(
        run_id="generated-id",
        call_id="generated-id",
        spec=HumanContactSpec(
            msg="what is your favorite color",
            channel=contact_channel,
        ),
        status=HumanContactStatus(response="magenta"),
    )

    tool = hl.human_as_tool(contact_channel)

    assert tool.__name__ == "contact_human_in_slack_in_a_dm_with_the_librarian"
    assert (
        tool.__doc__
        == """
    Contact a human via slack and wait for a response in a dm with the librarian
    """.strip()
    )

    ret = tool("what is your favorite color")

    assert ret == "magenta"

    contacts.add.assert_called_once_with(
        HumanContact(
            run_id="generated-id",
            call_id="generated-id",
            spec=HumanContactSpec(
                msg="what is your favorite color",
                channel=contact_channel,
            ),
        )
    )

    contacts.get.assert_called_once_with("generated-id")

    pass